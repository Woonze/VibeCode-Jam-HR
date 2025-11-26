TASK_BANK_PY = {
    "easy": [
        {
            "id": "py-easy-1",
            "title": "Сложение чисел",
            "description": "Напишите функцию add(a, b), возвращающую сумму.",
            "template": "def add(a, b):\n    pass\n\nprint(add(1, 2))"
        },
        {
            "id": "py-easy-2",
            "title": "Максимум из двух чисел",
            "description": "Напишите функцию max2(a, b), возвращающую большее число.",
            "template": "def max2(a, b):\n    pass\n\nprint(max2(3, 7))"
        },
        {
            "id": "py-easy-3",
            "title": "Количество гласных",
            "description": "Напишите функцию count_vowels(s), возвращающую количество гласных.",
            "template": "def count_vowels(s):\n    pass\n\nprint(count_vowels('hello'))"
        },
        {
            "id": "py-easy-4",
            "title": "Палиндром",
            "description": "Определите, является ли строка палиндромом.",
            "template": "def is_palindrome(s):\n    pass\n\nprint(is_palindrome('level'))"
        },
        {
            "id": "py-easy-5",
            "title": "Сумма списка",
            "description": "Реализуйте функцию sum_list(nums), возвращающую сумму элементов.",
            "template": "def sum_list(nums):\n    pass\n\nprint(sum_list([1,2,3]))"
        },
        {
            "id": "py-easy-6",
            "title": "Разворот строки",
            "description": "Напишите функцию reverse(s), разворачивающую строку.",
            "template": "def reverse(s):\n    pass\n\nprint(reverse('abc'))"
        },
        {
            "id": "py-easy-7",
            "title": "Уникальные элементы",
            "description": "Верните список уникальных элементов.",
            "template": "def unique(nums):\n    pass\n\nprint(unique([1,2,2,3]))"
        },
        {
            "id": "py-easy-8",
            "title": "Факториал",
            "description": "Напишите функцию factorial(n).",
            "template": "def factorial(n):\n    pass\n\nprint(factorial(5))"
        },
        {
            "id": "py-easy-9",
            "title": "Четное или нечётное",
            "description": "Верните 'even' или 'odd' для числа.",
            "template": "def even_odd(n):\n    pass\n\nprint(even_odd(4))"
        },
        {
            "id": "py-easy-10",
            "title": "Поиск минимума",
            "description": "Верните минимальное число в списке.",
            "template": "def find_min(nums):\n    pass\n\nprint(find_min([3,1,4]))"
        }
    ],

    "medium": [
        {
            "id": "py-med-1",
            "title": "Фибоначчи",
            "description": "Реализуйте рекурсивную или итеративную функцию fib(n).",
            "template": "def fib(n):\n    pass\n\nprint(fib(10))"
        },
        {
            "id": "py-med-2",
            "title": "Разворот списка",
            "description": "Реализуйте reverse_list без встроенного reversed().",
            "template": "def reverse_list(arr):\n    pass\n\nprint(reverse_list([1,2,3]))"
        },
        {
            "id": "py-med-3",
            "title": "Подсчет слов",
            "description": "Подсчитайте встречаемость слов в строке.",
            "template": "def count_words(text):\n    pass\n\nprint(count_words('a b a'))"
        },
        {
            "id": "py-med-4",
            "title": "Flatten списка",
            "description": "Реализуйте flatten для вложенных списков.",
            "template": "def flatten(lst):\n    pass\n\nprint(flatten([1,[2,[3]]]))"
        },
        {
            "id": "py-med-5",
            "title": "Анаграмма",
            "description": "Определите, являются ли строки анаграммами.",
            "template": "def is_anagram(a, b):\n    pass\n\nprint(is_anagram('listen','silent'))"
        },
        {
            "id": "py-med-6",
            "title": "Удаление дубликатов",
            "description": "Удалите дубликаты, сохранив порядок.",
            "template": "def dedupe(nums):\n    pass\n\nprint(dedupe([1,2,2,3,1]))"
        },
        {
            "id": "py-med-7",
            "title": "Два числа дают сумму",
            "description": "Вернуть индексы двух чисел, дающих сумму target.",
            "template": "def two_sum(nums, target):\n    pass\n\nprint(two_sum([2,7,11,15],9))"
        },
        {
            "id": "py-med-8",
            "title": "Слияние словарей",
            "description": "Реализуйте merge_dicts(d1, d2).",
            "template": "def merge_dicts(d1, d2):\n    pass\n\nprint(merge_dicts({'a':1},{'b':2}))"
        },
        {
            "id": "py-med-9",
            "title": "Баланс скобок",
            "description": "Проверить корректность скобочной последовательности.",
            "template": "def is_valid(s):\n    pass\n\nprint(is_valid('([])'))"
        },
        {
            "id": "py-med-10",
            "title": "Группировка по ключу",
            "description": "Сгруппируйте список словарей по значению ключа.",
            "template": "def group_by(items, key):\n    pass\n\nprint(group_by([{'t':1},{'t':2},{'t':1}], 't'))"
        }
    ],

    "hard": [
        {
            "id": "py-hard-1",
            "title": "LRU Cache",
            "description": "Реализуйте класс LRUCache.",
            "template": "class LRUCache:\n    pass"
        },
        {
            "id": "py-hard-2",
            "title": "Поиск пути в графе",
            "description": "Реализуйте DFS/BFS поиск пути между двумя вершинами.",
            "template": "def path_exists(graph, start, end):\n    pass"
        },
        {
            "id": "py-hard-3",
            "title": "Сортировка слиянием",
            "description": "Реализуйте merge_sort.",
            "template": "def merge_sort(arr):\n    pass"
        },
        {
            "id": "py-hard-4",
            "title": "Мини-ORM",
            "description": "Реализуйте простейшее хранение объектов и выборку по полям.",
            "template": "class MiniORM:\n    pass"
        },
        {
            "id": "py-hard-5",
            "title": "Дерево поиска",
            "description": "Реализуйте BST: insert, find, inorder.",
            "template": "class BST:\n    pass"
        },
        {
            "id": "py-hard-6",
            "title": "LRU с TTL",
            "description": "Реализуйте LRUCache с временем жизни ключей.",
            "template": "class LRUCacheTTL:\n    pass"
        },
        {
            "id": "py-hard-7",
            "title": "Топ-K элементов",
            "description": "Верните K самых больших элементов через heap.",
            "template": "def top_k(nums, k):\n    pass"
        },
        {
            "id": "py-hard-8",
            "title": "Алгоритм Дейкстры",
            "description": "Реализуйте dijkstra(graph, start).",
            "template": "def dijkstra(graph, start):\n    pass"
        },
        {
            "id": "py-hard-9",
            "title": "Парсер выражений",
            "description": "Реализуйте простой калькулятор: + - * / и скобки.",
            "template": "def calc(expr):\n    pass"
        },
        {
            "id": "py-hard-10",
            "title": "Мини-фреймворк событий",
            "description": "Реализуйте EventEmitter с on/off/emit.",
            "template": "class EventEmitter:\n    pass"
        }
    ]
}