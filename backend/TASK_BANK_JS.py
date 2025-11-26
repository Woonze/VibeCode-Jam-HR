TASK_BANK_JS = {

    # EASY — базовые задачи
    "easy": [
        {
            "id": "js-easy-1",
            "title": "Сортировка массива чисел",
            "description": (
                "Реализуйте функцию sortNumbers(arr), которая принимает массив чисел "
                "и возвращает новый массив, отсортированный по возрастанию. "
                "Нельзя использовать arr.sort()."
            ),
            "template": "function sortNumbers(arr) {\n  // Реализуйте сортировку вручную\n}\n",
        },
        {
            "id": "js-easy-2",
            "title": "Поиск минимального значения",
            "description": (
                "Напишите функцию minArr(arr), которая возвращает самое маленькое число в массиве. "
                "Решить без Math.min(...arr)."
            ),
            "template": "function minArr(arr) {\n  // Найдите минимум вручную\n}\n",
        },
        {
            "id": "js-easy-3",
            "title": "Подсчёт количества слов",
            "description": (
                "Создайте функцию countWords(str), которая принимает строку и возвращает "
                "количество слов в ней. Считайте, что слова разделяются одним пробелом."
            ),
            "template": "function countWords(str) {\n  // Подсчитайте количество слов\n}\n",
        },
        {
            "id": "js-easy-4",
            "title": "Проверка строки на палиндром",
            "description": (
                "Реализуйте функцию isPalindrome(str), которая проверяет, является ли строка "
                "палиндромом (одинаково читается слева направо и справа налево). Игнорируйте регистр."
            ),
            "template": "function isPalindrome(str) {\n  // Проверьте строку\n}\n",
        },
        {
            "id": "js-easy-5",
            "title": "Удаление дубликатов",
            "description": (
                "Напишите функцию removeDuplicates(arr), которая удаляет повторяющиеся элементы массива "
                "и возвращает новый массив только с уникальными значениями (сохраните порядок первых вхождений)."
            ),
            "template": "function removeDuplicates(arr) {\n  // Удалите дубликаты вручную\n}\n",
        },
        {
            "id": "js-easy-6",
            "title": "Сумма цифр числа",
            "description": (
                "Напишите функцию sumDigits(num), которая возвращает сумму всех цифр числа. "
                "Учтите, что num может быть отрицательным."
            ),
            "template": "function sumDigits(num) {\n  // Разбейте число на цифры и просуммируйте\n}\n",
        },
        {
            "id": "js-easy-7",
            "title": "Реверс массива",
            "description": (
                "Реализуйте функцию reverseArray(arr), которая возвращает новый массив "
                "с элементами в обратном порядке. Не используйте встроенный reverse()."
            ),
            "template": "function reverseArray(arr) {\n  // Переверните массив вручную\n}\n",
        },
        {
            "id": "js-easy-8",
            "title": "Фильтрация чётных чисел",
            "description": (
                "Создайте функцию filterEven(arr), возвращающую массив только из чётных чисел. "
                "Нечётные числа должны быть отброшены."
            ),
            "template": "function filterEven(arr) {\n  // Верните только чётные значения\n}\n",
        },
        {
            "id": "js-easy-9",
            "title": "Подсчёт гласных в строке",
            "description": (
                "Реализуйте функцию countVowels(str), возвращающую количество гласных букв в строке. "
                "Считайте гласными: a, e, i, o, u, а, е, ё, и, о, у, ы, э, ю, я."
            ),
            "template": "function countVowels(str) {\n  // Подсчитайте гласные\n}\n",
        },
        {
            "id": "js-easy-10",
            "title": "Частотный словарь массива",
            "description": (
                "Создайте функцию freq(arr), которая возвращает объект, где каждому "
                "элементу массива соответствует количество его вхождений."
            ),
            "template": "function freq(arr) {\n  // Верните объект вида {value: count}\n}\n",
        },
    ],

    # MEDIUM — структуры данных, строки, алгоритмы
    "medium": [
        {
            "id": "js-med-1",
            "title": "Группировка объектов по полю",
            "description": (
                "Реализуйте функцию groupBy(arr, key), которая группирует объекты массива arr "
                "по значению поля key. Результат — объект, где ключи это значения key, "
                "а значения — массивы объектов."
            ),
            "template": "function groupBy(arr, key) {\n  // Сгруппируйте элементы по ключу\n}\n",
        },
        {
            "id": "js-med-2",
            "title": "Проверка сбалансированности скобок",
            "description": (
                "Напишите функцию isBalanced(str), которая проверяет корректность скобок. "
                "Поддерживаемые скобки: (), {}, []. Используйте стек."
            ),
            "template": "function isBalanced(str) {\n  // Используйте стек\n}\n",
        },
        {
            "id": "js-med-3",
            "title": "Функция-кешер",
            "description": (
                "Реализуйте функцию memoize(fn), которая возвращает кешированную версию fn. "
                "Если fn уже вызывали с такими аргументами — верните результат из кеша."
            ),
            "template": "function memoize(fn) {\n  // Верните кешированную функцию\n}\n",
        },
        {
            "id": "js-med-4",
            "title": "Глубокое копирование объекта",
            "description": (
                "Напишите функцию deepClone(obj), которая выполняет глубокое копирование объекта "
                "любой вложенности без использования structuredClone или сторонних библиотек."
            ),
            "template": "function deepClone(obj) {\n  // Клонируйте вручную\n}\n",
        },
        {
            "id": "js-med-5",
            "title": "Удаление falsy-значений",
            "description": (
                "Создайте функцию cleanArray(arr), которая удаляет все falsy значения "
                "(false, 0, '', null, undefined, NaN)."
            ),
            "template": "function cleanArray(arr) {\n  // Отфильтруйте falsy значения\n}\n",
        },
        {
            "id": "js-med-6",
            "title": "Форматирование строки в camelCase",
            "description": (
                "Реализуйте функцию camelCase(str), которая преобразует строку вида "
                "'hello world example' в 'helloWorldExample'."
            ),
            "template": "function camelCase(str) {\n  // Преобразуйте строку в camelCase\n}\n",
        },
        {
            "id": "js-med-7",
            "title": "Плоский массив",
            "description": "Создайте функцию flatten(arr), которая превращает вложенный массив в плоский.",
            "template": "function flatten(arr) {\n  // Разверните вложенные массивы\n}\n",
        },
        {
            "id": "js-med-8",
            "title": "Перевод числа в римские цифры",
            "description": (
                "Реализуйте функцию toRoman(num), преобразующую положительное целое число "
                "в римскую запись (I, V, X, L, C, D, M)."
            ),
            "template": "function toRoman(num) {\n  // Преобразуйте число в римскую нотацию\n}\n",
        },
        {
            "id": "js-med-9",
            "title": "Фильтрация по диапазону",
            "description": (
                "Реализуйте filterRange(arr, min, max), возвращающую элементы между min и max (включительно). "
                "Результат — новый массив."
            ),
            "template": "function filterRange(arr, min, max) {\n  // Верните элементы диапазона\n}\n",
        },
        {
            "id": "js-med-10",
            "title": "Анализ строки (частоты символов)",
            "description": (
                "Напишите функцию charFrequency(str), возвращающую объект частот символов строки. "
                "Учитывайте регистр символов."
            ),
            "template": "function charFrequency(str) {\n  // Частоты символов\n}\n",
        },
    ],

    # HARD — паттерны, продвинутые структуры и алгоритмы
    "hard": [
        {
            "id": "js-hard-1",
            "title": "Throttle function",
            "description": (
                "Реализуйте функцию throttle(fn, delay), которая ограничивает вызов функции fn "
                "не чаще, чем раз в delay миллисекунд."
            ),
            "template": "function throttle(fn, delay) {\n  // Реализуйте throttle\n}\n",
        },
        {
            "id": "js-hard-2",
            "title": "EventEmitter",
            "description": (
                "Реализуйте класс EventEmitter, поддерживающий методы:\n"
                "on(event, handler), off(event, handler), emit(event, ...args)."
            ),
            "template": (
                "class EventEmitter {\n"
                "  constructor() {\n"
                "    this.events = {};\n"
                "  }\n"
                "  on(event, handler) {}\n"
                "  off(event, handler) {}\n"
                "  emit(event, ...args) {}\n"
                "}\n"
            ),
        },
        {
            "id": "js-hard-3",
            "title": "Deep Equal",
            "description": (
                "Реализуйте функцию deepEqual(a, b), которая сравнивает два значения "
                "любой вложенности на полное структурное равенство."
            ),
            "template": "function deepEqual(a, b) {\n  // Реализуйте глубокое сравнение\n}\n",
        },
        {
            "id": "js-hard-4",
            "title": "Свой Promise",
            "description": "Реализуйте класс MyPromise с методами then, catch, finally.",
            "template": (
                "class MyPromise {\n"
                "  constructor(executor) {}\n"
                "  then(onFulfilled, onRejected) {}\n"
                "  catch(onRejected) {}\n"
                "  finally(onFinally) {}\n"
                "}\n"
            ),
        },
        {
            "id": "js-hard-5",
            "title": "LRU Cache",
            "description": "Реализуйте структуру данных LRUCache с методами get(key) и put(key, value).",
            "template": (
                "class LRUCache {\n"
                "  constructor(capacity) {}\n"
                "  get(key) {}\n"
                "  put(key, value) {}\n"
                "}\n"
            ),
        },
        {
            "id": "js-hard-6",
            "title": "Шифрование Цезаря",
            "description": (
                "Реализуйте функцию caesarCipher(str, shift), которая шифрует строку "
                "сдвигом букв по алфавиту. Сохраните регистр."
            ),
            "template": "function caesarCipher(str, shift) {\n  // Реализуйте алгоритм\n}\n",
        },
        {
            "id": "js-hard-7",
            "title": "Мини-база данных в памяти",
            "description": (
                "Реализуйте класс MiniDB, поддерживающий методы insert(obj), find(query), "
                "update(query, patch), delete(query)."
            ),
            "template": (
                "class MiniDB {\n"
                "  constructor() {\n"
                "    this.data = [];\n"
                "  }\n"
                "  insert(obj) {}\n"
                "  find(query) {}\n"
                "  update(query, patch) {}\n"
                "  delete(query) {}\n"
                "}\n"
            ),
        },
        {
            "id": "js-hard-8",
            "title": "Планировщик задач",
            "description": (
                "Реализуйте функцию scheduler(tasks), где tasks — массив функций, "
                "и каждая функция должна выполняться строго после завершения предыдущей "
                "(поддержка async-функций)."
            ),
            "template": "function scheduler(tasks) {\n  // Запускайте функции последовательно\n}\n",
        },
        {
            "id": "js-hard-9",
            "title": "Parser mini-JS выражений",
            "description": (
                "Реализуйте функцию parseExpression(expr), которая принимает строку вида "
                "'2 + 3 * (4 - 1)' и вычисляет результат. Требуется реализовать парсер "
                "с поддержкой скобок и приоритетов операций."
            ),
            "template": "function parseExpression(expr) {\n  // Реализуйте парсер выражений\n}\n",
        },
        {
            "id": "js-hard-10",
            "title": "Своя реализация Redux Store",
            "description": (
                "Реализуйте createStore(reducer), возвращающую объект с методами "
                "getState(), dispatch(action), subscribe(listener)."
            ),
            "template": "function createStore(reducer) {\n  // Реализуйте Redux-подобный store\n}\n",
        },
    ],
}