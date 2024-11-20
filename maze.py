import tkinter as tk
from tkinter import messagebox
from queue import PriorityQueue
import time
import heapq

# Các node là các ô di chuyển: node -> '.'
# Các cạnh là các node kề nhau ngoài trừ '#'.
# Chi phí là là 1.

# Kích thước ô
CELL_SIZE = 50

# Màu sắc đại diện
COLORS = {
    '#': 'black',   # Tường
    '.': 'white',   # Đường đi
    '$': 'green',   # Bụi cây
    'S': 'blue',    # Điểm bắt đầu
    'G': 'red',     # Điểm mục tiêu
    'P': 'yellow',  # Người chạy
    'V': 'lightblue'  # Dấu vết
}
original_maze = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', 'S', '.', '.', '#', '.', '.', '$', '.', '#'],
    ['#', '#', '#', '.', '#', '.', '#', '#', '.', '#'],
    ['#', '.', '.', '.', '$', '.', '#', '.', '.', '#'],
    ['#', '.', '#', '#', '#', '$', '#', '.', '#', '#'],
    ['#', '.', '.', '.', '#', '.', '$', '.', '.', '#'],
    ['#', '#', '#', '.', '#', '#', '#', '#', '$', '#'],
    ['#', '.', '#', '.', '.', '.', '.', '#', '$', '#'],
    ['#', '.', '.', '#', '#', '#', '.', '.', 'G', '#'],
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
]

# Mê cung mẫu
maze = [
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
    ['#', 'S', '.', '.', '#', '.', '.', '$', '.', '#'],
    ['#', '#', '#', '.', '#', '.', '#', '#', '.', '#'],
    ['#', '.', '.', '.', '$', '.', '#', '.', '.', '#'],
    ['#', '.', '#', '#', '#', '$', '#', '.', '#', '#'],
    ['#', '.', '.', '.', '#', '.', '$', '.', '$', '#'],
    ['#', '#', '#', '.', '#', '#', '#', '#', '$', '#'],
    ['#', '.', '#', '.', '.', '.', '.', '#', '.', '#'],
    ['#', '.', '.', '#', '#', '#', '.', '.', 'G', '#'],
    ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#']
]
# Thuật toán UCS

def uniform_cost_search(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    
    # Initialize the open set (priority queue) using heapq
    frontier = []
    heapq.heappush(frontier, (0, start))  # (cost, position)
    
    # Initialize came_from and g_score
    came_from = {}
    g_score = {start: 0}

    while frontier:
        # Pop the node with the lowest cost (priority)
        current_cost, current = heapq.heappop(frontier)
        print(f"Current node: {current}, Cost: {current_cost}")  # In chi phí của node hiện tại

        # If we reached the goal, reconstruct the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]

            return path[::-1]  # Return the path from start to goal
        

        x, y = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (x + dx, y + dy)
            if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] != '#':
                if maze[neighbor[0]][neighbor[1]] == '$':
                    cost = 2
                else:
                    cost = 1
                tentative_g_score = g_score[current] + cost
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    heapq.heappush(frontier, (tentative_g_score, neighbor))  # Push new state into the frontier

    return None  # If no solution is found

# Hàm Heuristic (Manhattan)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Hàm hcost để lấy chi phí heuristic của đường đi
def hcost(path, goal):
    last_node = path[-1]  # lấy node cuối cùng trong đường đi path
    h_cost = heuristic(last_node, goal)  # tính chi phí heuristic (Manhattan distance)
    print(f"Node: {last_node}, Heuristic Cost: {h_cost}")  # In chi phí heuristic của node hiện tại
    return h_cost, last_node

# Thuật toán Greedy Search
def greedy_search(maze, start, goal):
    rows, cols = len(maze), len(maze[0])
    visited = set()  # Lưu trữ các node đã thăm để tránh vòng lặp
    queue = [[start]]  # Lưu trữ các đường đi (mỗi đường đi là một danh sách các node)
    
    while queue:
        queue.sort(key=lambda path: hcost(path, goal)[0])  # Sắp xếp theo chi phí heuristic (Manhattan distance)
        
        path = queue.pop(0)  # Lấy đường đi có heuristic thấp nhất
        current_node = path[-1]  # Lấy node cuối cùng trong đường đi
        
        if current_node in visited:
            continue
        else:
            visited.add(current_node)
            if current_node == goal:
                return path  # Trả về đường đi từ start -> goal
            
            # Duyệt các ô kề
            x, y = current_node
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (x + dx, y + dy)
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and maze[neighbor[0]][neighbor[1]] != '#':
                    
                    if neighbor not in visited:
                        new_path = path.copy()
                        new_path.append(neighbor)  # Thêm node kề vào đường đi
                        queue.append(new_path)
    
    return None  # Nếu không tìm thấy đường đi


# Lớp giao diện
class MazeApp(tk.Tk):
    def __init__(self, maze):
        super().__init__()
        self.title("Maze Solver with A*, UCS, and Greedy")
        self.maze = maze
        self.canvas = tk.Canvas(self, width=len(maze[0]) * CELL_SIZE, height=len(maze) * CELL_SIZE)
        self.canvas.pack()
        self.render_maze()

    def render_maze(self):
        """Hiển thị mê cung."""
        self.canvas.delete("all")
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                x0, y0 = j * CELL_SIZE, i * CELL_SIZE
                x1, y1 = x0 + CELL_SIZE, y0 + CELL_SIZE
                color = COLORS.get(cell, 'white')
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline='black')


    def solve_ucs(self):
        """Giải mê cung bằng UCS và hiển thị kết quả."""
        start = self.find_position('S')
        goal = self.find_position('G')

        path = uniform_cost_search(self.maze, start, goal)
        self.display_path(path)

    def solve_greedy(self):
        """Giải mê cung bằng thuật toán Greedy và hiển thị kết quả."""
        start = self.find_position('S')
        goal = self.find_position('G')

        path = greedy_search(self.maze, start, goal)
        self.display_path(path)

    def display_path(self, path):
        if path:
            for step in path:
                x, y = step
                # Chỉ thay đổi các ô không phải là bụi cây ('S', 'G', '$')
                if self.maze[x][y] not in ['S', 'G', '$']:
                    self.maze[x][y] = 'P'  # Đánh dấu người chạy
                self.render_maze()
                self.update()
                time.sleep(0.3)  # Tạm dừng để quan sát
                # Đánh dấu dấu vết
                if self.maze[x][y] != '$':  # Nếu không phải bụi cây, thì đánh dấu dấu vết
                    self.maze[x][y] = 'V'
            messagebox.showinfo("Success", "Maze solved!")
        else:
            messagebox.showerror("Error", "No solution found!")



    def find_position(self, symbol):
        """Tìm vị trí của ký hiệu (ví dụ 'S' hoặc 'G')."""
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                if cell == symbol:
                    return (i, j)
        return None

    def restart_maze(self):
        """Khôi phục lại mê cung ban đầu."""
        global maze
        self.maze = [row[:] for row in original_maze]  # Sử dụng bản sao của mê cung ban đầu
        self.render_maze()


# Chạy ứng dụng
if __name__ == "__main__":
    app = MazeApp(maze)

    solve_ucs_button = tk.Button(app, text="Solve with UCS", command=app.solve_ucs)
    solve_ucs_button.pack()

    solve_greedy_button = tk.Button(app, text="Solve with Greedy", command=app.solve_greedy)
    solve_greedy_button.pack()

    restart_button = tk.Button(app, text="Restart Maze", command=app.restart_maze)
    restart_button.pack()

    app.mainloop()