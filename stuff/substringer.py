from typing import Dict

class Solution:
    def lengthOfLongestSubstring(self, s:str) -> int:
        print(f"--- {s} ---")
        longest_possible = int(len(s) / 2)
        possibilities = {}
        for current_length in range(2, longest_possible + 1):
            new_possibilities = self.find_substring(string_obj=s, length=current_length, possibilities=possibilities)
            if len(new_possibilities) == 0: break
            possibilities = new_possibilities
        print(f"REPEATER={possibilities}")
        print(f"longest possible in {s}({len(s)})={longest_possible}")
        print(f"")
        return -1
    @classmethod
    def find_substring(cls, string_obj:str, length:int, possibilities:Dict[str, int]):
        subs = {}
        # for offset in range(0, length):
        # for i in range(0 + offset, len(string_obj), length):
        for i in range(0, len(string_obj), 1):
            start = i
            end = i + length
            sub = string_obj[start:end]
            is_sub_candidate = any(map(lambda x: sub.startswith(x), possibilities))
            print(f"[{string_obj}][({len(string_obj)})][{start}:{end}] {sub} >> {is_sub_candidate}")
            if len(possibilities) == 0 or is_sub_candidate:
                # print(f"[{string_obj}][offset={offset}][i={i}] {sub}")
                subs[sub] = 1 if subs.get(sub) is None else (subs[sub] + 1)
        subs = dict(sorted(subs.items(), key=lambda x: x[1], reverse=True))
        print(f"ordered subs={subs}")
        subs = dict(filter(lambda x: x[1] > 1, subs.items()))
        print(f"filtered subs={subs}")
        return subs
def check_strings():
    strings = [
        "abcxabc",
        "abcxommabcxiabcxozz",
        "abcdef",
    ]
    solution = Solution()
    [solution.lengthOfLongestSubstring(s=x) for x in strings]
    return
def main():
    check_strings()
    return
if __name__ == "__main__":
    main()




