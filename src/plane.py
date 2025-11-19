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
    def __init__(
        self,
        num_rows,
        arrangement=defaultArrangement,
        exemptions=None,
        bin_capacity_per_row=4,
        aisle_shape="▦▦",
        num_doors: int = 1,
        doors: list = None,  # type: ignore
        num_lanes: int = None,  # type: ignore
    ):
        """
        num_rows   (int): Number of rows on plane
        arrangement (list): e.g. ['A','B','C','aisle','D','E','F']
        exemptions (list[tuple]): seats to pre-occupy, e.g. [(15,'A'),(15,'F')]
        """
        self.num_rows = int(num_rows)
        self.arrangement = arrangement
        self.exemptions = exemptions or []
        self.seat_map = {}
        self.generated = False
        self.overhead_bins = {
            r: bin_capacity_per_row for r in range(1, self.num_rows + 1)
        }
        # Visual representation for aisle cells (and entrance L-shape)
        # Default is a double-line block '══' but can be customized
        self.aisle_cell = aisle_shape

        # Doors and lanes
        # num_doors: 1 or 2 (front, rear). `doors` can explicitly name doors
        # e.g. ['front','rear'] or ['front'].
        self.num_doors = max(1, int(num_doors))
        self.doors = doors or (["front", "rear"] if self.num_doors == 2 else ["front"])
        # num_lanes: if provided, will enforce that many aisle lanes; otherwise
        # it will be inferred from how many 'aisle' tokens appear in `arrangement`.
        self.requested_num_lanes = num_lanes
        # Internal representation: list of aisle lanes. Each lane is a list of
        # length num_rows+1 where index 0 is the entrance slot for that lane.
        self.aisles = []
        # Backwards compatibility: plane.aisle references the primary (first) lane
        self.aisle = None

    def generate_plane(self):
        """Build seats and apply exemptions."""
        if self.generated:
            return self
        # Determine number of lanes from arrangement unless explicitly set
        arrangement_aisles = [
            i for i, t in enumerate(self.arrangement) if t.lower() == "aisle"
        ]
        inferred_lanes = max(1, len(arrangement_aisles))
        lanes = self.requested_num_lanes or inferred_lanes

        # Create aisles: each lane has an entrance slot index 0 + row slots 1..N
        self.aisles = [[None for _ in range(self.num_rows + 1)] for _ in range(lanes)]

        # Backwards-compatibility alias: primary aisle refers to first lane
        self.aisle = self.aisles[0]

        # Generate seats
        for r in range(1, self.num_rows + 1):
            for token in self.arrangement:
                if token.lower() != "aisle":
                    s = Seat(r, token)
                    self.seat_map[(r, token)] = s
        # Apply exemptions
        for r, L in self.exemptions:
            seat = self.seat_map.get((r, L))
            if seat:
                seat.occupied = True

        self.generated = True
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
        if not self.generated:
            raise RuntimeError("Call generate_plane() before show_plane().")

        def fmt_cell(s, w=6):
            return str(s).center(w)

        # Header row (include optional entrance columns at left and right)
        header = (
            "Seat ".ljust(6)
            + fmt_cell("ENTL")
            + "".join(fmt_cell(r) for r in range(1, self.num_rows + 1))
        )
        if "rear" in self.doors:
            header += fmt_cell("ENTR")
        print(header)
        print("-" * len(header))

        # Each seat letter (or aisle) is one row in the printed chart
        # Map each 'aisle' occurrence in arrangement to a lane index
        aisle_occurrences = [
            i for i, t in enumerate(self.arrangement) if t.lower() == "aisle"
        ]
        # For printing, we'll iterate arrangement tokens; keep a counter for which lane to render
        lane_counter = 0

        for token in self.arrangement:
            row_cells = []
            # Left entrance column symbol (front door)
            ent_left = "↓" if "front" in self.doors else ""
            row_cells.append(fmt_cell(ent_left))

            for r in range(1, self.num_rows + 1):
                if token.lower() == "aisle":
                    # Render the corresponding lane if available
                    if lane_counter < len(self.aisles):
                        # Choose arrow direction: prefer front-> (→) if front door exists,
                        # otherwise rear <- (←). If both, show ↔.
                        if "front" in self.doors and "rear" in self.doors:
                            cell = "↔"
                        elif "front" in self.doors:
                            cell = "→"
                        elif "rear" in self.doors:
                            cell = "←"
                        else:
                            cell = "→"
                    else:
                        cell = " "
                else:
                    seat = self.seat_map[(r, token)]
                    if mode == "status":
                        cell = "[X]" if seat.occupied else "[ ]"
                    elif mode == "ids":
                        cell = f"{r}{token}" + ("*" if seat.occupied else "")
                    else:
                        raise ValueError("mode must be 'status' or 'ids'")
                row_cells.append(fmt_cell(cell))

            # Right entrance column symbol (rear door) appended if applicable
            if "rear" in self.doors:
                ent_right = "↑" if "rear" in self.doors else ""
                row_cells.append(fmt_cell(ent_right))

            print(fmt_cell(token, 6) + "".join(row_cells))
            print()
        if mode == "status":
            print(f"[ ] = empty   [X] = occupied   → = aisle")
        else:
            print(f"* after seat ID = occupied     → = aisle")

    def try_stow_bag(self, row):
        """
        Attempt to stow a carry-on bag in overhead bin at `row`.
        Returns True if success, False if that row is full.
        """
        if self.overhead_bins[row] > 0:
            self.overhead_bins[row] -= 1
            return True
        return False

    # Helper properties for multi-door / multi-lane support
    @property
    def num_lanes(self):
        return len(self.aisles) if self.aisles else 1

    def entrances(self):
        """Return a mapping describing entrance positions for doors.

        Returns a dict mapping door name ('front'/'rear') to list of (lane_idx, pos_idx)
        where pos_idx is 0 for front entrance and num_rows for rear entrance.
        """
        out = {}
        for d in self.doors:
            if d == "front":
                out.setdefault(d, [(lane_idx, 0) for lane_idx in range(self.num_lanes)])
            elif d == "rear":
                out.setdefault(
                    d, [(lane_idx, self.num_rows) for lane_idx in range(self.num_lanes)]
                )
        return out


# -------------------------------
# Standard Example with 10 seats
# -------------------------------
if __name__ == "__main__":
    emergency_exits = [(5, "A"), (5, "F")]
    plane = Plane(
        10, arrangement=defaultArrangement, exemptions=emergency_exits
    ).generate_plane()

    # Show the full plane
    plane.show_plane(mode="status")
