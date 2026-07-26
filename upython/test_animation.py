import unittest
import sys

# Mock modules
class MockPin:
    OUT = 1
    def __init__(self, *args, **kwargs): pass
    def off(self): pass
    def on(self): pass

class MockSPI:
    def __init__(self, *args, **kwargs): pass
    def write(self, data): pass

class MockTimer:
    PERIODIC = 1
    def __init__(self, *args, **kwargs): pass
    def init(self, *args, **kwargs): pass

class MockMachine:
    Pin = MockPin
    SPI = MockSPI
    Timer = MockTimer

sys.modules['machine'] = MockMachine

# Define animation logic to test
buffram = [0] * 8
def clear_buffer():
    for i in range(8):
        buffram[i] = 0

def draw_line(state, pos):
    clear_buffer()
    if state == 0 or state == 2:
        mask = 1 << pos
        for i in range(8):
            buffram[i] = mask
    elif state == 1 or state == 3:
        buffram[pos] = 0xFF

line_state = 0
line_pos = 0
def move_line():
    global line_state, line_pos
    if line_state == 0:  # Down
        if line_pos < 7: line_pos += 1
        else: line_state = 1; line_pos = 0
    elif line_state == 1:  # Right
        if line_pos < 7: line_pos += 1
        else: line_state = 2; line_pos = 7
    elif line_state == 2:  # Up
        if line_pos > 0: line_pos -= 1
        else: line_state = 3; line_pos = 7
    elif line_state == 3:  # Left
        if line_pos > 0: line_pos -= 1
        else: line_state = 0; line_pos = 0

class TestLineAnimation(unittest.TestCase):
    def setUp(self):
        global line_state, line_pos
        clear_buffer()
        line_state = 0
        line_pos = 0

    def test_draw_row(self):
        draw_line(0, 3) # Row at pos 3
        expected = 1 << 3
        for val in buffram:
            self.assertEqual(val, expected)

    def test_draw_col(self):
        draw_line(1, 4) # Col at pos 4
        for i in range(8):
            if i == 4:
                self.assertEqual(buffram[i], 0xFF)
            else:
                self.assertEqual(buffram[i], 0)

    def test_move_transitions(self):
        global line_state, line_pos
        # State 0 -> 1
        line_pos = 7
        move_line()
        self.assertEqual(line_state, 1)
        self.assertEqual(line_pos, 0)
        
        # State 1 -> 2
        line_pos = 7
        move_line()
        self.assertEqual(line_state, 2)
        self.assertEqual(line_pos, 7)

        # State 2 -> 3
        line_pos = 0
        move_line()
        self.assertEqual(line_state, 3)
        self.assertEqual(line_pos, 7)

        # State 3 -> 0
        line_pos = 0
        move_line()
        self.assertEqual(line_state, 0)
        self.assertEqual(line_pos, 0)

if __name__ == '__main__':
    unittest.main()
