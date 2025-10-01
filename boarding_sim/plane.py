import numpy as np

class Seat:
    def __init__(self, row, letter):
        self.row = row
        self.letter = letter
        self.occupied = False
        
    def show_status(self):
        status = "occupied." if self.occupied else "not occupied."
        print(f"Seat {self.row}{self.letter} is {status}")

    def __repr__(self):
        return f"Seat {self.row}{self.letter}"

defaultArrangement = ["A", "B", "C", "aisle", "D", "E", "F"]

class Plane:
    def __init__(self, num_rows, arrangement=defaultArrangement, exemptions=None):
        """
        num_rows   (int): Number of rows on plane
        arrangement (list): e.g. ['A','B','C','aisle','D','E','F']
        exemptions (list[tuple]): seats to pre-occupy, e.g. [(15,'A'),(15,'F')]
        """
        self.num_rows = int(num_rows)
        self.arrangement = arrangement
        self.exemptions = exemptions or []
        self.seat_map = {}
        self._generated = False

    def generate_plane(self):
        """Build seats and apply exemptions."""
        if self._generated:
            return self

        for r in range(1, self.num_rows + 1):
            for token in self.arrangement:
                if token.lower() != "aisle":
                    s = Seat(r, token)
                    self.seat_map[(r, token)] = s
        # Apply exemptions
        for (r, L) in self.exemptions:
            seat = self.seat_map.get((r, L))
            if seat:
                seat.occupied = True

        self._generated = True
        return self

    def occupy(self, row, letter):
        s = self.seat_map.get((row, letter))
        if s and not s.occupied:
            s.occupied = True
            return True
        return False

    def show_plane(self, mode="status"):
        """
        Show the plane with rows as columns (rotated view).
        Row numbers go left-to-right, seat letters go top-to-bottom.
        mode: 'status' ([ ] vs [X]) or 'ids' (seat IDs, with * if occupied)
        """
        if not self._generated:
            raise RuntimeError("Call generate_plane() before show_plane().")

        def fmt_cell(s, w=6): return str(s).center(w)

        # Header row
        header = "Seat ".ljust(6) + "".join(fmt_cell(r) for r in range(1, self.num_rows + 1))
        print(header)
        print("-" * len(header))

        # Each seat letter (or aisle) is one row in the printed chart
        for token in self.arrangement:
            row_cells = []
            for r in range(1, self.num_rows + 1):
                if token.lower() == "aisle":
                    cell = "││"
                else:
                    seat = self.seat_map[(r, token)]
                    if mode == "status":
                        cell = "[X]" if seat.occupied else "[ ]"
                    elif mode == "ids":
                        cell = f"{r}{token}" + ("*" if seat.occupied else "")
                    else:
                        raise ValueError("mode must be 'status' or 'ids'")
                row_cells.append(fmt_cell(cell))
            print(fmt_cell(token, 6) + "".join(row_cells))

        print()
        if mode == "status":
            print("[ ] = empty   [X] = occupied   ││ = aisle")
        else:
            print("* after seat ID = occupied     ││ = aisle")

# -------------------------
# Standard Example with 10 seats
# -------------------------
if __name__ == "__main__":
    emergency_exits = [(5, 'A'), (5, 'F')]
    plane = Plane(10, arrangement=defaultArrangement, exemptions=emergency_exits).generate_plane()

    # Show the full plane
    plane.show_plane(mode="status")