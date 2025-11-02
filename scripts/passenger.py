import random

class Passenger:
    def __init__(self, pid, target_row, target_letter):
        self.pid = pid
        self.target_row = target_row          # 1-based row number
        self.target_letter = target_letter    # 'A', 'B', etc.

        self.aisle_pos = -1                   # -1 = not yet entered plane
        self.seated = False

        # NEW: overhead bin behavior
        self.has_bag = random.random() < 0.8  # e.g. 80% of pax have a carry-on
        self.active_delay = 0                 # how many ticks I'm currently blocking aisle
        self.done_stowing = False             # did I already put my bag up?

    def step(self, plane):
        # already seated, nothing to do
        if self.seated:
            return

        # haven't entered the plane yet: try to step into row 1 aisle (index 0)
        if self.aisle_pos == -1:
            if plane.aisle[0] is None:
                self.aisle_pos = 0
                plane.aisle[0] = self
            return

        dest_idx = self.target_row - 1  # convert seat row to aisle index

        # If I'm still walking to my row
        if self.aisle_pos < dest_idx:
            next_idx = self.aisle_pos + 1
            if plane.aisle[next_idx] is None:
                # move forward
                plane.aisle[self.aisle_pos] = None
                self.aisle_pos = next_idx
                plane.aisle[self.aisle_pos] = self
            return

        # I am now at my row
        if self.aisle_pos == dest_idx:
            # If I'm currently stowing or otherwise blocking, count down
            if self.active_delay > 0:
                self.active_delay -= 1
                return

            # Haven't stowed yet and I have a bag → try stowing
            if self.has_bag and not self.done_stowing:
                if plane.try_stow_bag(self.target_row):
                    # Bin had space, stow is quick but not instant
                    self.active_delay = random.randint(1, 2)
                    self.done_stowing = True
                    return
                else:
                    # Bin ABOVE my row is full.
                    # Super simple model: I spend extra time figuring it out.
                    # (In reality you'd walk backward to stash in earlier row.
                    # For MVP we just block longer right here.)
                    self.active_delay = random.randint(3, 5)
                    self.done_stowing = True  # after this delay, assume it's "handled"
                    return

            # Either no bag OR bag is already stowed → sit down
            plane.aisle[self.aisle_pos] = None
            plane.seat_passenger(self.target_row, self.target_letter)
            self.seated = True
            return