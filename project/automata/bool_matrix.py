from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy import sparse


class BoolMatrix:
    """Represents a bool matrix by nondeterministic
    finite automaton

    This class represents a bool matrix, where epsilon \
    symbols are forbidden.

    Parameters
    ----------
    nfa : NondeterministicFiniteAutomaton, optional
        NFA to initialize bool matrix

    **Attributes:**

    Each bool matrix contains set of states, set of starting states,
    set of final states, and state:index dictionary.
    By default, these are empty but can be filled from the inputted NFA

    """

    def __init__(self, nfa: NondeterministicFiniteAutomaton = None):
        """Initialize a bool matrix with inputted NFA

        Parameters
        ----------
        nfa : NondeterministicFiniteAutomaton, optional
            NFA to initialize bool matrix

        """
        self.start_states, self.final_states = set(), set()
        self.states, self.matrices = dict(), dict()

        if nfa is None:
            return

        for i, state in enumerate(nfa.states):
            self.states[state] = i
        for state in nfa.start_states:
            self.start_states.add(self.states[state])
        for state in nfa.final_states:
            self.final_states.add(self.states[state])

        num_of_states = len(self.states)

        for start_state, transitions in nfa.to_dict().items():
            for symbol, finish_states in transitions.items():
                if isinstance(finish_states, State):
                    finish_states = {finish_states}

                for finish_state in finish_states:
                    if symbol not in self.matrices:
                        self.matrices[symbol] = sparse.csr_matrix(
                            (num_of_states, num_of_states), dtype=bool
                        )

                    self.matrices[symbol][
                        self.states[start_state], self.states[finish_state]
                    ] = True

    def intersect(self, another: "BoolMatrix") -> "BoolMatrix":
        """Intersects a bool matrix with another bool matrix using the tensor product

        Parameters
        ----------
        another : BoolMatrix
            Another bool matrix to intersect

        Returns
        ----------
        result : BoolMatrix
            Matrix equal to tensor product of self and another matrix

        """
        result = BoolMatrix()

        for symbol in self.matrices.keys() & another.matrices.keys():
            result.matrices[symbol] = sparse.kron(
                self.matrices[symbol], another.matrices[symbol], format="csr"
            )

        for self_state, self_index in self.states.items():
            for other_state, other_index in another.states.items():
                result_state = self_index * len(another.states) + other_index
                result.states[(self_state, other_state)] = result_state

                if (
                    self_index in self.start_states
                    and other_index in another.start_states
                ):
                    result.start_states.add(result_state)

                if (
                    self_index in self.final_states
                    and other_index in another.final_states
                ):
                    result.final_states.add(result_state)

        return result

    def transitive_closure(self) -> sparse.csr_matrix:
        """
        Returns the transitive closure of the given bool matrix

        Returns
        ----------
        result : sparse.csr_matrix
            Transitive closure of bool matrix

        """
        if len(self.matrices) == 0:
            return sparse.csr_matrix((0, 0), dtype=bool)

        num_of_states = len(self.states)
        result = sum(
            self.matrices.values(),
            start=sparse.csr_array((num_of_states, num_of_states), dtype=bool),
        )

        prev_nnz = 0
        while result.nnz != prev_nnz:
            prev_nnz = result.nnz
            result += result @ result

        return result

    def to_nfa(self) -> NondeterministicFiniteAutomaton:
        """Transforms bool matrix into NFA

        Returns
        ----------
        nfa : NondeterministicFiniteAutomaton
            NFA that equivalent to bool matrix

        """
        nfa = NondeterministicFiniteAutomaton()
        for symbol, matrix in self.matrices.items():
            for start_state, finish_state in zip(*matrix.nonzero()):
                nfa.add_transition(start_state, symbol, finish_state)

        for state in self.start_states:
            nfa.add_start_state(state)

        for state in self.final_states:
            nfa.add_final_state(state)

        return nfa
