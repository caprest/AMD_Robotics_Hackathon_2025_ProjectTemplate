import curses
from threading import Lock


class KeyboardState:
    """
    Tracks key presses inside a terminal using curses.
    No root, no X11/Wayland required.

    Uses "sticky" mode: the last note key pressed remains active
    until a different note key is pressed or space is pressed to stop.
    """

    # Keys that should be "sticky" (note keys)
    STICKY_KEYS = {ord("c"), ord("e"), ord("g")}

    def __init__(self, stdscr):
        self._pressed = set()
        self._current_note_key = None  # Sticky note key
        self._lock = Lock()
        self.stdscr = stdscr

        curses.cbreak()
        self.stdscr.nodelay(True)
        self.stdscr.keypad(True)

    def poll(self):
        """
        Poll terminal for keys.
        Call this each frame in your loop.
        """
        key = self.stdscr.getch()
        while key != -1:
            with self._lock:
                self._pressed.add(key)

                # Update sticky note key if a note key was pressed
                if key in self.STICKY_KEYS:
                    self._current_note_key = key
                # Space bar clears the sticky note
                elif key == ord(" "):
                    self._current_note_key = None

            key = self.stdscr.getch()

    def is_pressed(self, key):
        """
        Returns True if a key is currently registered as pressed.
        Accepts either an integer keycode or a single character string.
        """
        if isinstance(key, str):
            if key == "esc":
                keycode = 27
            elif len(key) == 1:
                keycode = ord(key)
            else:
                raise ValueError(f"Invalid key string: {key}")
        else:
            keycode = key

        with self._lock:
            return keycode in self._pressed

    def get_current_note_key(self) -> str | None:
        """
        Returns the currently active note key (sticky).
        Returns None if no note is active (space was pressed).
        """
        with self._lock:
            if self._current_note_key is None:
                return None
            return chr(self._current_note_key)

    def clear(self):
        """Clear pressed keys each frame (but keep sticky note)."""
        with self._lock:
            self._pressed.clear()


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    import time

    def main(stdscr):
        ks = KeyboardState(stdscr)
        stdscr.addstr(0, 0, "Press 'a' to test, ESC to quit.")
        stdscr.refresh()

        while True:
            ks.poll()

            if ks.is_pressed("a"):
                stdscr.addstr(1, 0, "A is pressed!")
                stdscr.refresh()

            if ks.is_pressed("esc"):
                stdscr.addstr(2, 0, "ESC pressed, exiting.")
                stdscr.refresh()
                time.sleep(0.5)
                break

            ks.clear()
            time.sleep(0.05)

    curses.wrapper(main)
