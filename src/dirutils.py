# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, see
# <http://www.gnu.org/licenses/>.



"""
Utility module for discovering the differences between two directory
trees

author: Christopher O'Brien  <obriencj@gmail.com>
license: LGPL
"""



LEFT = "left only"
RIGHT = "right only"
DIFF = "changed"
SAME = "same"
BOTH = SAME # meh, synonyms




def fnmatches(entry, *pattern_list):
    from fnmatch import fnmatch
    for pattern in pattern_list:
        if pattern and fnmatch(entry, pattern):
            return True
    return False



def compare(left, right):

    """ generator emiting pairs indicating the contents of the left
    and right directories. The pairs are in the form of (difference,
    filename) where difference is one of the LEFT, RIGHT, DIFF, or
    BOTH constants. This generator recursively walks both trees."""

    from filecmp import dircmp
    
    dc = dircmp(left, right, ignore=[])
    return _gen_from_dircmp(dc, len(left), len(right))
    
    


def _gen_from_dircmp(dc, ltrim, rtrim):
    from os.path import isdir, join
    from os import walk

    left_only = dc.left_only
    left_only.sort()
    
    for f in left_only:
        fp = join(dc.left, f)
        if isdir(fp):
            for r,d,fs in walk(fp):
                r = r[ltrim:]
                for f in fs:
                    #print r, f
                    yield(LEFT, join(r, f))
        else:
            yield (LEFT, fp[ltrim:]) #join(dc.left[ltrim:], f))
        
    right_only = dc.right_only
    right_only.sort()

    for f in right_only:
        fp = join(dc.right, f)
        if isdir(fp):
            for r,d,fs in walk(fp):
                r = r[rtrim:]
                for f in fs:
                    #print r, f
                    yield(RIGHT, join(r, f))
        else:
            yield (RIGHT, fp[rtrim:]) #join(dc.right[rtrim:], f))

    diff_files = dc.diff_files
    diff_files.sort()

    for f in diff_files:
        yield (DIFF, join(dc.right[rtrim:], f))

    same_files = dc.same_files
    same_files.sort()

    for f in same_files:
        yield (BOTH, join(dc.left[ltrim:], f))

    subdirs = dc.subdirs.values()
    subdirs.sort()
    for sub in subdirs:
        for event in _gen_from_dircmp(sub, ltrim, rtrim):
            yield event



def collect_compare(left, right):
    return collect_compare_into(left, right, [], [], [], [])



def collect_compare_into(left, right, added, removed, altered, same):

    for event,file in compare(left, right):
        
        if event == LEFT:
            group = removed
        elif event == RIGHT:
            group = added
        elif event == DIFF:
            group = altered
        elif event == BOTH:
            group = same
        else:
            assert(False)

        if group is not None:
            group.append(file)

    return added,removed,altered,same



#
# The end.