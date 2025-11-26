TEST_BANK_JS = {

    # EASY
    "js-easy-1": {  # sortNumbers
        "visible": [
            {"input": [[3,1,2]], "expected": [1,2,3]},
            {"input": [[5,5,1]], "expected": [1,5,5]},
            {"input": [[10,-1,0]], "expected": [-1,0,10]},
        ],
        "hidden": [
            {"input": [[100,50,75]], "expected": [50,75,100]},
            {"input": [[9,8,7,6]], "expected": [6,7,8,9]},
        ]
    },

    "js-easy-2": {  # minArr
        "visible": [
            {"input": [[3,7,1]], "expected": 1},
            {"input": [[10,5,6]], "expected": 5},
            {"input": [[-1,-9,-3]], "expected": -9},
        ],
        "hidden": [
            {"input": [[42,42]], "expected": 42},
            {"input": [[100,200,0]], "expected": 0},
        ]
    },

    "js-easy-3": {  # countWords
        "visible": [
            {"input": ["a b c"], "expected": 3},
            {"input": ["hello world"], "expected": 2},
            {"input": ["one"], "expected": 1},
        ],
        "hidden": [
            {"input": ["two words"], "expected": 2},
            {"input": ["x x x x"], "expected": 4},
        ]
    },

    "js-easy-4": {  # isPalindrome
        "visible": [
            {"input": ["level"], "expected": True},
            {"input": ["abba"], "expected": True},
            {"input": ["hello"], "expected": False},
        ],
        "hidden": [
            {"input": ["RaceCar"], "expected": True},
            {"input": ["abcba"], "expected": True},
        ]
    },

    "js-easy-5": {  # removeDuplicates
        "visible": [
            {"input": [[1,2,2,3]], "expected": [1,2,3]},
            {"input": [[1,1,1]], "expected": [1]},
            {"input": [[3,2,1]], "expected": [3,2,1]},
        ],
        "hidden": [
            {"input": [[5,5,4,4,3]], "expected": [5,4,3]},
            {"input": [[10,9,10,8]], "expected": [10,9,8]},
        ]
    },

    "js-easy-6": {  # sumDigits
        "visible": [
            {"input": [123], "expected": 6},
            {"input": [-99], "expected": 18},
            {"input": [0], "expected": 0},
        ],
        "hidden": [
            {"input": [456], "expected": 15},
            {"input": [-12345], "expected": 15},
        ]
    },

    "js-easy-7": {  # reverseArray
        "visible": [
            {"input": [[1,2,3]], "expected": [3,2,1]},
            {"input": [[1]], "expected": [1]},
            {"input": [[1,2]], "expected": [2,1]},
        ],
        "hidden": [
            {"input": [[5,4,3,2]], "expected": [2,3,4,5]},
            {"input": [[10,20,30]], "expected": [30,20,10]},
        ]
    },

    "js-easy-8": {  # filterEven
        "visible": [
            {"input": [[1,2,3,4]], "expected": [2,4]},
            {"input": [[2,2,2]], "expected": [2,2,2]},
            {"input": [[1,3,5]], "expected": []},
        ],
        "hidden": [
            {"input": [[10,11,12]], "expected": [10,12]},
            {"input": [[0,9,-2]], "expected": [0,-2]},
        ]
    },

    "js-easy-9": {  # countVowels
        "visible": [
            {"input": ["hello"], "expected": 2},
            {"input": ["xyz"], "expected": 0},
            {"input": ["aaa"], "expected": 3},
        ],
        "hidden": [
            {"input": ["привет"], "expected": 2},
            {"input": ["aeiouAEIOU"], "expected": 10},
        ]
    },

    "js-easy-10": {  # freq
        "visible": [
            {"input": [[1,1,2]], "expected": {"1":2,"2":1}},
            {"input": [["a","a","b"]], "expected": {"a":2,"b":1}},
            {"input": [[True,True,False]], "expected": {"true":2,"false":1}},
        ],
        "hidden": [
            {"input": [[3,3,3]], "expected": {"3":3}},
            {"input": [["x","y","x","z"]], "expected": {"x":2,"y":1,"z":1}},
        ]
    },

    # -------------------------------------------------
    # MEDIUM
    # -------------------------------------------------

    "js-med-1": {  # groupBy
        "visible": [
            {
                "input": [[{"a":1},{"a":2},{"a":1}], "a"],
                "expected": {"1":[{"a":1},{"a":1}], "2":[{"a":2}]}
            },
            {
                "input": [[{"x":10},{"x":10}], "x"],
                "expected": {"10":[{"x":10},{"x":10}]}
            },
            {
                "input": [[{"k":1}], "k"],
                "expected": {"1":[{"k":1}]}
            }
        ],
        "hidden": [
            {
                "input": [[{"a":3},{"a":3},{"a":2}], "a"],
                "expected": {"3":[{"a":3},{"a":3}],"2":[{"a":2}]}
            }
        ]
    },

    "js-med-2": {  # isBalanced
        "visible": [
            {"input": ["([])"], "expected": True},
            {"input": ["()[]{}"], "expected": True},
            {"input": ["([)]"], "expected": False},
        ],
        "hidden": [
            {"input": ["((()))"], "expected": True},
            {"input": ["([{}{}])"], "expected": True},
        ]
    },

    "js-med-3": {  # memoize
        "visible": [
            {"input": [], "expected": "memo basic"},  
        ],
        "hidden": []
    },

    "js-med-4": {  # deepClone
        "visible": [
            {"input": [{"a":1,"b":{"c":2}}], "expected": {"a":1,"b":{"c":2}}},
        ],
        "hidden": []
    },

    "js-med-5": {  # cleanArray
        "visible": [
            {"input": [[0,1,False,2,'',3]], "expected": [1,2,3]},
            {"input": [["a",None,""]], "expected": ["a"]},
            {"input": [["NaN",5]], "expected": [5]},
        ],
        "hidden": [
            {"input": [[None,7,0]], "expected": [7]},
        ]
    },

    "js-med-6": {  # camelCase
        "visible": [
            {"input": ["hello world"], "expected": "helloWorld"},
            {"input": ["a b c"], "expected": "aBC"},
            {"input": ["java script language"], "expected": "javaScriptLanguage"},
        ],
        "hidden": [
            {"input": ["multiple   spaces"], "expected": "multipleSpaces"},
        ]
    },

    "js-med-7": {  # flatten
        "visible": [
            {"input": [[1,[2,[3]]]], "expected": [1,2,3]},
            {"input": [[[]]], "expected": []},
            {"input": [[1,2,3]], "expected": [1,2,3]},
        ],
        "hidden": [
            {"input": [[1,[2,[3,[4]]]]], "expected": [1,2,3,4]},
        ]
    },

    "js-med-8": {  # toRoman
        "visible": [
            {"input": [1], "expected": "I"},
            {"input": [4], "expected": "IV"},
            {"input": [9], "expected": "IX"},
        ],
        "hidden": [
            {"input": [58], "expected": "LVIII"},
            {"input": [199], "expected": "CXCIX"},
        ]
    },

    "js-med-9": {  # filterRange
        "visible": [
            {"input": [[1,2,3,4],2,3], "expected": [2,3]},
            {"input": [[10,20,30],10,20], "expected": [10,20]},
        ],
        "hidden": [
            {"input": [[5,6,7,8],6,8], "expected": [6,7,8]},
        ]
    },

    "js-med-10": {  # charFrequency
        "visible": [
            {"input": ["abca"], "expected": {"a":2,"b":1,"c":1}},
            {"input": ["HELLO"], "expected": {"H":1,"E":1,"L":2,"O":1}},
        ],
        "hidden": [
            {"input": ["xxx"], "expected": {"x":3}},
        ]
    },

    # -------------------------------------------------
    # HARD
    # -------------------------------------------------

    "js-hard-1": {
        "visible": [{"input": [], "expected": "throttle basic"}],
        "hidden": []
    },

    "js-hard-2": {  # EventEmitter
        "visible": [{"input": [], "expected": "emitter basic"}],
        "hidden": []
    },

    "js-hard-3": {  # deepEqual
        "visible": [
            {"input": [{"a":1},{"a":1}], "expected": True},
            {"input": [{"a":1},{"a":2}], "expected": False},
        ],
        "hidden": []
    },

    "js-hard-4": {
        "visible": [{"input": [], "expected": "promise basic"}],
        "hidden": []
    },

    "js-hard-5": {
        "visible": [{"input": [], "expected": "lru basic"}],
        "hidden": []
    },

    "js-hard-6": {  # Caesar
        "visible": [
            {"input": ["abc",1], "expected": "bcd"},
            {"input": ["xyz",2], "expected": "zab"},
        ],
        "hidden": [
            {"input": ["Hello",1], "expected": "Ifmmp"},
        ]
    },

    "js-hard-7": {  # MiniDB
        "visible": [{"input": [], "expected": "minidb basic"}],
        "hidden": []
    },

    "js-hard-8": {
        "visible": [{"input": [], "expected": "scheduler basic"}],
        "hidden": []
    },

    "js-hard-9": {  # parseExpression
        "visible": [
            {"input": ["1+2*3"], "expected": 7},
            {"input": ["(2+3)*4"], "expected": 20},
        ],
        "hidden": []
    },

    "js-hard-10": {
        "visible": [{"input": [], "expected": "redux basic"}],
        "hidden": []
    },
}
