import json
import argparse
from abc import ABC, abstractmethod

# 抽象产品
class Visualizer(ABC):
    @abstractmethod
    def visualize(self, data: dict) -> str:
        pass

# 具体产品
class TreeVisualizer(Visualizer):
    def __init__(self, icon_family):
        self.icon_family = icon_family

    def visualize(self, data: dict, indent: str = '', last: bool = True) -> str:
        output = ''
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                is_last = (i == len(items) - 1)
                output += indent
                if is_last:
                    output += '└─'
                    next_indent = indent + '   '
                else:
                    output += '├─'
                    next_indent = indent + '│  '
                
                if isinstance(value, dict):
                    output += f"{self.icon_family['node']}{key}\n"
                    output += self.visualize(value, next_indent, is_last)
                else:
                    output += f"{self.icon_family['leaf']}{key}"
                    if value is not None:
                        output += f": {value}"
                    output += "\n"
        return output

# class RectVisualizer(Visualizer):
#     def __init__(self, icon_family):
#         self.icon_family = icon_family

#     def visualize(self, data: dict) -> str:
#         output, _ = self._visualize(data)
#         return output

#     def _visualize(self, data: dict, level: int = 0, parent_key: str = None) -> tuple[str, int]:
#         if not isinstance(data, dict):
#             return '', level

#         max_width = 0
#         lines = []
#         for key, value in data.items():
#             if isinstance(value, dict):
#                 child_output, child_width = self._visualize(value, level + 1, key)
#                 lines.append((f"{self.icon_family['node']}{key}", child_output))
#                 max_width = max(max_width, len(key) + 2 + child_width)
#             else:
#                 line = f"{self.icon_family['leaf']}{key}"
#                 if value is not None:
#                     line += f": {value}"
#                 lines.append((line, ''))
#                 max_width = max(max_width, len(line))

#         border_line = f"┌{'─' * (max_width+2)}┐"
#         result = [border_line]
#         for i, (line, child_output) in enumerate(lines):
#             result.append(f"│ {line.ljust(max_width)} │")
#             if child_output:
#                 child_lines = child_output.split('\n')
#                 for child_line in child_lines:
#                     if child_line:
#                         result.append(f"│ {child_line.ljust(max_width)} │")
#         result.append(f"└{'─' * (max_width+2)}┘")
#         return '\n'.join(result), max_width
    
class RectVisualizer(Visualizer):
    def __init__(self, icon_family):
        self.icon_family = icon_family
        self.is_begin=True

    def visualize(self, data: dict) -> str:
        output, _ = self._visualize(data)
        return output

    def _visualize(self, data: dict, level: int = 0, indent: str = '', parent_key: str = None) -> tuple[str, int]:
        if not isinstance(data, dict):
            return '', level

        max_width = 0
        lines = []
        for key, value in data.items():
            if isinstance(value, dict):
                child_output, child_width = self._visualize(value, level + 1, key)
                lines.append((f"{self.icon_family['node']}{key}", child_output))
                max_width = max(max_width, len(key) + 2 + child_width)
            else:
                line = f"{self.icon_family['leaf']}{key}"
                if value is not None:
                    line += f": {value}"
                lines.append((line, ''))
                max_width = max(max_width, len(line))

        output = ''
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                is_last = (i == len(items) - 1)
                output += indent
                if is_last:
                    output += '└─'
                    next_indent = indent + '   '
                else:
                    output += '├─'
                    next_indent = indent + '│  '
                
                if isinstance(value, dict):
                    output += f"{self.icon_family['node']}{key}\n"
                    output += self.visualize(value, next_indent, is_last)
                else:
                    output += f"{self.icon_family['leaf']}{key}"
                    if value is not None:
                        output += f": {value}"
                    output += "\n"
        return '\n'.join(output), max_width
    
# 抽象工厂
class VisualizerFactory(ABC):
    @abstractmethod
    def create_visualizer(self) -> Visualizer:
        pass

# 具体工厂
class TreeVisualizerFactory(VisualizerFactory):
    def __init__(self, icon_family):
        self.icon_family = icon_family

    def create_visualizer(self) -> Visualizer:
        return TreeVisualizer(self.icon_family)

class RectVisualizerFactory(VisualizerFactory):
    def __init__(self, icon_family):
        self.icon_family = icon_family

    def create_visualizer(self) -> Visualizer:
        return RectVisualizer(self.icon_family)

# 客户端代码
def main():
    parser = argparse.ArgumentParser(description="JSON File Visualizer")
    parser.add_argument('-f', '--file', required=True, help='Path to the JSON file')
    parser.add_argument('-s', '--style', required=True, choices=['tree', 'rect'], help='Visualization style')
    parser.add_argument('-i', '--icon', required=True, choices=['poker', 'emoji'], help='Icon family')

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        data = json.load(f)

    poker_icon_family = {
        'node': '♢',
        'leaf': '♤'
    }

    emoji_icon_family = {
        'node': '📁',
        'leaf': '📄'
    }

    icon_families = {
        'poker': poker_icon_family,
        'emoji': emoji_icon_family
    }

    factory_classes = {
        'tree': TreeVisualizerFactory,
        'rect': RectVisualizerFactory
    }

    icon_family = icon_families[args.icon]
    factory_class = factory_classes[args.style]

    factory = factory_class(icon_family)
    visualizer = factory.create_visualizer()

    output = visualizer.visualize(data)
    print(output)

if __name__ == '__main__':
    main()