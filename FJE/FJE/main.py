import json
import argparse
from abc import ABC, abstractmethod
from collections.abc import Iterator, Iterable

# 迭代器模式
class JSONIterator(Iterator):
    def __init__(self, data):
        self.stack = [(None, data)]
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if not self.stack:
            raise StopIteration
        key, value = self.stack.pop()
        if isinstance(value, dict):
            self.stack.extend(reversed(list(value.items())))
        return key, value

# 策略模式
class Visualizer(ABC):
    @abstractmethod
    def visualize(self, iterator: JSONIterator) -> str:
        pass

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

class BlockVisualizer(Visualizer):
    def __init__(self, icon_family):
        self.icon_family = icon_family

    def visualize(self, data: dict) -> str:
        output, _ = self._visualize(data)
        return output

    def _visualize(self, data: dict, level: int = 0, parent_key: str = None) -> tuple[str, int]:
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
                line = f"{self.icon_family['leaf']}{key}: {value}" if value is not None else f"{self.icon_family['leaf']}{key}"
                lines.append((line, ''))
                max_width = max(max_width, len(line))

        border_line_top = f"┌{'─' * (max_width+2)}┐" if level == 0 else f"┌{'─' * (max_width+2)}┐"
        border_line_bottom = f"└{'─' * (max_width+2)}┘" if level == 0 else f"└{'─' * (max_width+2)}┘"
        
        result = [border_line_top]
        for i, (line, child_output) in enumerate(lines):
            result.append(f"│ {line.ljust(max_width)} │")
            if child_output:
                child_lines = child_output.split('\n')
                for child_line in child_lines:
                    if child_line:
                        result.append(f"│ {child_line.ljust(max_width)} │")
        result.append(border_line_bottom)
        return '\n'.join(result), max_width

class RectVisualizer(Visualizer):
    def __init__(self, icon_family):
        self.icon_family = icon_family
        self.is_begin=True

    def visualize(self, data: dict) -> str:
        max_width = self._calculate_max_width(data)
        output=self._visualize(data,max_width)
        last_line=output.split('\n')[-2]
        end=''
        i=0
        while i < len(last_line):
            if last_line[i:i+3]=='│  ':
                end+='└──'
                i=i+3
            elif last_line[i]=='├':
                end+='┴'
                i+=1
            elif last_line[i]=='┤':
                end+='┘'
                i+=1
            else:
                end+=last_line[i]
                i+=1
        output=output.split('\n')
        res=''
        for i in range(len(output)):
            if i==len(output)-2:
                res+=end
                res+='\n'
            else:
                res+=output[i]
                res+='\n'
        return res

    def _calculate_max_width(self, data: dict, level: int = 0) -> int:
        max_width = 0
        if isinstance(data, dict):
            for key, value in data.items():
                line_length = len(f"{self.icon_family['node']}{key}") + 1
                if value is not None:
                    if isinstance(value, dict):
                        child_width = self._calculate_max_width(value, level + 1)
                        line_length = max(line_length, child_width)
                    else:
                        line_length += len(f": {value}") + 1
                max_width = max(max_width, line_length)
        return max_width + 10  # Adding buffer for borders and spaces

    def _visualize(self, data: dict, max_width: int, indent: str = '', depth: int = 0) -> str:
        output = ''
        if isinstance(data, dict):
            items = list(data.items())
            for i, (key, value) in enumerate(items):
                line=''
                if self.is_begin and i==0 :
                    line = f"{indent}┌─{self.icon_family['leaf'] if not isinstance(value, dict) else self.icon_family['node']}{key}"
                    self.is_begin = False
                    output += f"{line} {'─' * (max_width - len(line) - 6)}┐\n"
                else:
                    line = f"{indent}{'│  '*depth}├─{self.icon_family['leaf'] if not isinstance(value, dict) else self.icon_family['node']}{key}{': '+value if isinstance(value,str) else ''}"
                    output += f"{line} {'─' * (max_width - len(line) - 6)}┤\n"
                
                if isinstance(value, dict):
                    output += self._visualize(value, max_width, indent, depth+1)
        return output

# 策略上下文
class VisualizerContext:
    def __init__(self, strategy: Visualizer):
        self.strategy = strategy

    def set_strategy(self, strategy: Visualizer):
        self.strategy = strategy

    def visualize(self, data: dict) -> str:
        # iterator=JSONIterator(data)
        return self.strategy.visualize(data)

# 客户端代码
def main():
    parser = argparse.ArgumentParser(description="JSON File Visualizer")
    parser.add_argument('-f', '--file', required=True, help='Path to the JSON file')
    parser.add_argument('-s', '--style', required=True, choices=['tree', 'rect', 'block'], help='Visualization style')
    parser.add_argument('-i', '--icon', required=True, choices=['poker', 'emoji'], help='Icon family')

    args = parser.parse_args()

    with open(args.file, 'r') as f:
        data = json.load(f)

    poker_icon_family = {
        'node': '♢',
        'leaf': '♤'
    }

    emoji_icon_family = {
        'node': '۞',
        'leaf': '¤'
    }

    icon_families = {
        'poker': poker_icon_family,
        'emoji': emoji_icon_family
    }

    strategies = {
        'tree': TreeVisualizer,
        'rect': RectVisualizer,
        'block' : BlockVisualizer,
    }

    icon_family = icon_families[args.icon]
    strategy_class = strategies[args.style]

    strategy = strategy_class(icon_family)
    context = VisualizerContext(strategy)

    output = context.visualize(data)
    print(output)
    print(type(data))

if __name__ == '__main__':
    main()