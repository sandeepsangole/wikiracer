from py_wikiracer.internet import Internet
from typing import List
import re
from collections import defaultdict
import heapq as heap


class Parser:

    # def getLinks(page):
    #     match = 'href="/wiki/[A-Z]+[^:\s]+."'
    #     links = re.findall(match, page)
    #     prefix = 'href="/wiki/'
    #     for i in range(0, len(links)):
    #         links[i] = links[i][len(prefix):len(links[i]) - 1]
    #     return links

    @staticmethod
    def get_links_in_page(html: str) -> List[str]:
        """
        In this method, we should parse a page's HTML and return a list of links in the page.
        Be sure not to return any link with a DISALLOWED character.
        All links should be of the form "/wiki/<page name>", as to not follow external links
        """
        links = []
        disallowed = Internet.DISALLOWED
        # disallowed
        links = re.findall('href="/wiki/[,()/.A-z?<_!&%\s=>0-9;-]+"', html)
        disallowed_str = ''.join(disallowed)
        prefix = 'href="/wiki/'
        href_str = 'href="'
        new_lst = []
        for link in links:
            link = link.replace('"', '')

            if link not in new_lst:
                link_name = link[len(prefix) - 1:]
                if not Parser.containsAny(link_name, disallowed) and link[len(href_str) - 1:] not in new_lst:
                    new_lst.append(link[len(href_str) - 1:])

        # YOUR CODE HERE
        # You can look into using regex, or just use Python's find methods to find the <a> tags or any other identifiable features
        # A good starting place is to print out `html` and look for patterns before/after the links that you can string.find().
        # Make sure your list doesn't have duplicates. Return the list in the same order as they appear in the HTML.
        # This function will be stress tested so make it efficient!
        return new_lst

    def containsAny(link, disallowed):
        if link == 'Tan_/_Qin_(surname_%E8%A6%83)':
            print(link)

        for c in disallowed:
            if c in link:
                print(c, link)
                return 1
        return 0


# In these methods, we are given a source page and a goal page, and we should return
#  the shortest path between the two pages. Be careful! Wikipedia is very large.

# These are all very similar algorithms, so it is advisable to make a global helper function that does all of the work, and have
#  each of these call the helper with a different data type (stack, queue, priority queue, etc.)

class BFSProblem:
    def __init__(self):
        self.internet = Internet()
        self.visited = []
        self.shortest_path = []
        self.queue = []

    # Example in/outputs:
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computer_science") == ["/wiki/Computer_science"]
    #  bfs(source = "/wiki/Computer_science", goal = "/wiki/Computation") == ["/wiki/Computer_science", "/wiki/Computation"]
    # Find more in the test case file.

    # Do not try to make fancy optimizations here. The autograder depends on you following standard BFS and will check all of the pages you download.
    # Links should be inserted into the queue as they are located in the page, and should be obtained using Parser's get_links_in_page.
    # Be very careful not to add things to the "visited" set of pages too early. You must wait for them to come out of the queue first. See if you can figure out why.
    #  This applies for bfs, dfs, and dijkstra's.
    # Download a page with self.internet.get_page().
    def bfs(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):

        # YOUR CODE HERE
        found = False
        path = [source]

        if source == goal:
            self.internet.get_page(source)
            return path + [goal]

        self.visited.append(source)
        self.queue.append((source, [source]))
        while self.queue:
            page, shortest_path = self.queue.pop(0)
            print(page, end=" ")
            html = self.internet.get_page(page)
            links = Parser.get_links_in_page(html)
            print(links)
            for link in links:
                if link == goal:
                    self.visited.append(goal)
                    return shortest_path + [goal]
                if link not in self.visited:
                    self.visited.append(link)
                    self.queue.append((link, shortest_path + [link]))

        return None


class DFSProblem:
    def __init__(self):
        self.internet = Internet()
        self.visited = []

    # Links should be inserted into a stack as they are located in the page. Do not add things to the visited list until they are taken out of the stack.
    def dfs(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        # YOUR CODE HERE
        path = []

        if source == goal:
            self.internet.get_page(source)
            return [source] + [goal]

        self.dfs_iterative(source, goal, path)

        if len(path) < 2:
            return None
        else:
            return path


    def def_util1(self, source, goal, path) -> bool:
        self.visited.append(source)
        path.append(source)

        if source == goal:
            return True

        html = self.internet.get_page(source)
        links = Parser.get_links_in_page(html)
        for link in links:
            if link not in self.visited:
                if self.def_util1(link, goal, path):
                    return True

        path.pop()

        return False

    def def_util(self, source, goal):
        html = self.internet.get_page(source)
        links = Parser.get_links_in_page(html)
        for link in links:
            if link == goal:
                return
            elif link not in self.visited:
                print
                'visiting: ' + link
                self.visited.append(link)
                self.def_util(link, goal)
                # self.visited.pop()
                return
            else:
                pass
        # self.visited.pop()

    def dfs_iterative(self, source, goal, path):
        stack = []
        # self.visited.append(source)
        stack.append(source)

        while len(stack) > 0:
            top = stack.pop()
            self.visited.append(top)
            path.append(top)
            html = self.internet.get_page(top)
            links = Parser.get_links_in_page(html)
            for link in links:
                if link == goal:
                    path.append(goal)
                    return
                if link not in self.visited:
                    stack.append(link)


class DijkstrasProblem:
    def __init__(self):
        self.internet = Internet()
        self.visited = set()

    # Links should be inserted into the heap as they are located in the page.
    # By default, the cost of going to a link is the length of a particular destination link's name. For instance,
    #  if we consider /wiki/a -> /wiki/ab, then the default cost function will have a value of 8.
    # This cost function is overridable and your implementation will be tested on different cost functions. Use costFn(node1, node2)
    #  to get the cost of a particular edge.
    # You should return the path from source to goal that minimizes the total cost. Assume cost > 0 for all edges.
    def dijkstras(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia", costFn=lambda x, y: len(y)):
        path = [source]

        if source == goal:
            self.internet.get_page(source)
            return path + [goal]

        pq = []
        nodeCosts = defaultdict(lambda: float('inf'))
        nodeCosts[source] = 0
        heap.heappush(pq, (0, source, [source]))
        while pq:
            _, current, shortest_path = heap.heappop(pq)

            self.visited.add(current)

            html = self.internet.get_page(current)
            links = Parser.get_links_in_page(html)

            for neighbour in links:
                weight = costFn(current, neighbour)
                if neighbour in self.visited:
                    continue

                newCost = nodeCosts[current] + weight

                if neighbour == goal:
                    return shortest_path +[goal]

                if nodeCosts[neighbour] > newCost:
                    nodeCosts[neighbour] = newCost
                    heap.heappush(pq, (newCost, neighbour, shortest_path +[neighbour]))

        return None

    def calculate_cost(self, current, links, costfun):
        weights = []
        for link in links:
            weights.append(costfun(current, link))

        return weights


class WikiracerProblem:
    def __init__(self):
        self.internet = Internet()

    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

    def wikiracer(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        path = [source]
        # YOUR CODE HERE
        # ...
        path.append(goal)
        return path  # if no path exists, return None


# KARMA
class FindInPageProblem:
    def __init__(self):
        self.internet = Internet()

    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source="/wiki/Calvin_Li", query=["ham", "cheese"]):
        raise NotImplementedError("Karma method find_in_page")

        path = [source]

        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path  # if no path exists, return None
