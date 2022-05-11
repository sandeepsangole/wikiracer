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
        links = re.findall('href="/wiki/[^?#:/\s]+"', html)
        disallowed_str = ''.join(disallowed)
        prefix = 'href="/wiki/'
        href_str = 'href="'
        new_lst = []
        for link in links:
            link = link.replace('"', '')
            next_page = link.replace('href=', '')
            if next_page not in new_lst:
                new_lst.append(next_page)

        # YOUR CODE HERE
        # You can look into using regex, or just use Python's find methods to find the <a> tags or any other identifiable features
        # A good starting place is to print out `html` and look for patterns before/after the links that you can string.find().
        # Make sure your list doesn't have duplicates. Return the list in the same order as they appear in the HTML.
        # This function will be stress tested so make it efficient!
        return new_lst


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
            # print(page, end=" ")
            html = self.internet.get_page(page)
            links = Parser.get_links_in_page(html)
            # print(links)
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
                    return shortest_path + [goal]

                if nodeCosts[neighbour] is None or nodeCosts[neighbour] > newCost:
                    nodeCosts[neighbour] = newCost
                    heap.heappush(pq, (newCost, neighbour, shortest_path + [neighbour]))

        return None


class WikiracerProblem:
    def __init__(self):
        self.internet = Internet()
        self.visited = set()
        self.matched = []
        # self.visited = []
        # self.shortest_path = []
        # self.queue = []
        self.low_priority = ['isbn_(identifier)', 'the_guardian', 'main_page', 'viaf_(identifier)', 'italy',
                             'geographic_coordinate_system', 'iran', 'time_zone', 'daylight_saving_time',
                             'persian_language', 'geonet_names_server', 'capital_city', 'united_states', 'manhattan',
                             'europe', 'wayback_machine', 'isni_(identifier)', 'sudoc_(identifier)', 'india',
                             'australia', 'painting', 'united_states_army', 'union_army', 'american_civil_war',
                             'find_a_grave', 'the_hollywood_reporter', 'imdb', 'cricket', 'first-class_cricket',
                             'forward_(association_football)', 'association_football', 'mexico', 'puerto_rico',
                             'canada', 'france', 'czech_republic', 'germany', 'switzerland', 'belgium', 'south_korea',
                             'hungary', 'netherlands', 'croatia', 'luxembourg', 'denmark', 'london', 'united_kingdom',
                             'batting_average_(cricket)', 'delivery_(cricket)', 'wicket', 'bowling_average',
                             'five-wicket_haul', 'stumped', 'issn_(identifier)', 'ireland', 'kazakhstan',
                             'russian_language', 'u.s._state', 'united_states_geological_survey', 'hebrew_language',
                             'israel', 'communes_of_france', 'regions_of_france', 'departments_of_france',
                             'arrondissements_of_france', 'cantons_of_france', 'central_european_time',
                             'central_european_summer_time', 'insee_code',
                             'institut_national_de_la_statistique_et_des_%c3%a9tudes_%c3%a9conomiques', 'beijing',
                             'china', 'given_name', 'world_war_i', 'spanish_language', 'soviet_union', 'world_war_ii',
                             'sweden', 'norway', 'the_london_gazette', 'trove_(identifier)', 'taxonomy_(biology)',
                             'animalia', 'lepidoptera', 'binomial_nomenclature', 'moth', 'wikidata',
                             'encyclopedia_of_life', 'global_biodiversity_information_facility',
                             'interim_register_of_marine_and_nonmarine_genera', 'the_global_lepidoptera_names_index',
                             'oclc_(identifier)', 'united_states_house_of_representatives', 'new_york_(state)',
                             'new_york_city', 'republican_party_(united_states)', 'alma_mater', 'yale_university',
                             'new_york_times', 'internet_archive', 'epoch_(astronomy)', 'bibcode_(identifier)',
                             'doi_(identifier)', 's2cid_(identifier)', 'japan', 'osaka', 'tokyo', 'japanese_language',
                             'music_genre', 'record_label', 'venezuela', 'surname', '2000_summer_olympics', 'spain',
                             'greece', 'brazil', 'egypt', 'portugal', 'poland', 'slovenia', 'austria', 'serbia',
                             'pmid_(identifier)', 'historic_districts_in_the_united_states', 'contributing_property',
                             'national_register_of_historic_places', 'national_park_service', 'animal', 'mollusca',
                             'synonym_(taxonomy)', 'species', 'pmc_(identifier)', 'barcode_of_life_data_system',
                             'inaturalist', 'integrated_taxonomic_information_system',
                             'national_center_for_biotechnology_information', 'world_register_of_marine_species',
                             'plant', 'vascular_plant', 'flowering_plant', 'peru', 'wikispecies',
                             'international_plant_names_index', 'plants_of_the_world_online', 'tropicos',
                             'world_flora_online', 'conservation_status', 'iucn_red_list', 'eudicots',
                             'countries_of_the_world', 'voivodeships_of_poland', 'powiat', 'gmina', 'german_language',
                             'village', 'basketball', 'the_times', 'bbc', 'eastern_european_summer_time', 'romania',
                             'new_jersey', 'the_new_york_times', 'states_and_territories_of_india',
                             'list_of_districts_of_india', 'hindi_language', 'indian_standard_time', 'census',
                             'sri_lanka', 'guitar', 'bass_guitar', 'estonia', 'latvia', 'russia', 'finland', 'ukraine',
                             'belarus', 'nigeria', 'utc%2b2', 'utc%2b3', 'defender_(association_football)',
                             'midfielder', 'captain_(association_football)', 'american_football', 'college_football',
                             'england', 'list_of_sovereign_states', 'telephone_numbering_plan',
                             'geographic_names_information_system', 'population_density', 'marriage', 'poverty_line',
                             'united_states_census_bureau', 'county_seat', 'city', 'town', 'census-designated_place',
                             'unincorporated_area', 'album', 'los_angeles', 'record_producer', 'single_(music)',
                             'allmusic', 'studio_album', 'mbrg_(identifier)', 'arthropod', 'insect', 'beetle', 'paris',
                             'washington_(state)', 'great_depression', 'baseball', 'tennis', 'california',
                             'mba_(identifier)', 'university_of_oxford', 'bachelor_of_arts', 'canadians',
                             'variety_(magazine)', 'democratic_party_(united_states)', 'incumbent',
                             'national_register_of_historic_places_listings_in_california', 'san_francisco', 'allmusic',
                             'twitter', 'national_biodiversity_network', 'new_zealand', 'malaysia', 'south_africa',
                             'thailand', 'argentina', 'turkey', 'boston', 'united_states_senate', 'the_plant_list',
                             'singapore', 'united_nations', 'united_states_navy', 'texas', 'discogs',
                             'national_register_of_historic_places_listings_in_pennsylvania', 'keeper_of_the_register',
                             'history_of_the_national_register_of_historic_places',
                             'national_register_of_historic_places_property_types', 'philippines', 'precipitation',
                             'wales', 'los_angeles_times', 'vehicle_registration_plate',
                             'simplified_chinese_characters', 'traditional_chinese_characters', 'pinyin', 'hong_kong',
                             'chordate', 'fossilworks', 'international_olympic_committee', 'pitcher',
                             'earned_run_average', 'major_league_baseball', 'melbourne', 'ontario', 'washington,_d.c.',
                             'utc%2b1', 'associated_press', 'pop_music', 'nepal', 'songwriter', 'country_music',
                             'family_(biology)', 'united_states_marine_corps', 'philadelphia', 'brooklyn',
                             'arabic_language', 'atlanta', 'spanish_name', 'french_language', 'florida',
                             'british_columbia', 'conservative_party_(uk)', 'parliament_of_the_united_kingdom',
                             'wikisource', 'public_domain', 'youtube', 'jazz', 'berlin', 'bulgaria', 'outfielder',
                             'batting_average_(baseball)', 'toronto', 'billboard_(magazine)', 'scotland',
                             'united_states_dollar', 'colombia', 'facebook', 'bill_mallon', 'sports_reference',
                             'demonym', 'indiana', 'national_register_of_historic_places_listings_in_alabama',
                             'national_register_of_historic_places_listings_in_kansas',
                             'national_register_of_historic_places_listings_in_new_jersey',
                             'national_register_of_historic_places_listings_in_south_carolina',
                             'national_register_of_historic_places_listings_in_the_marshall_islands',
                             'historic_england', 'uruguay', 'north_carolina', 'urban_area', 'buddhism',
                             'ordnance_survey_national_grid', 'virginia', 'michigan', 'jstor_(identifier)',
                             'the_washington_post', 'utc-5', 'pakistan']

    # Time for you to have fun! Using what you know, try to efficiently find the shortest path between two wikipedia pages.
    # Your only goal here is to minimize the total amount of pages downloaded from the Internet, as that is the dominating time-consuming action.

    # Your answer doesn't have to be perfect by any means, but we want to see some creative ideas.
    # One possible starting place is to get the links in `goal`, and then search for any of those from the source page, hoping that those pages lead back to goal.

    # Note: a BFS implementation with no optimizations will not get credit, and it will suck.
    # You may find Internet.get_random() useful, or you may not.

    def wikiracer(self, source="/wiki/Calvin_Li", goal="/wiki/Wikipedia"):
        # path = self.bidirectional_bfs(source, goal)
        path = self.utilize_dijk(source, goal)
        # print("PATH", path)
        return path  # if no path exists, return None

    def calculateCost(self, link, goal, no_prefix_g_links):
        prefix = "/wiki/"
        link = link[len(prefix):].lower()

        if link == 'main_page':
            return 2000

        if link in self.low_priority and link in no_prefix_g_links:
            return 3
        elif link in no_prefix_g_links:
            return 0
        elif link in self.low_priority:
            return 1000
        else:
            if '_' in link:
                cost = self.split_links(link, no_prefix_g_links,'_')
                if cost:
                    return cost
            elif ' ' in link:
                cost =  self.split_links(link, no_prefix_g_links,' ')
                if cost:
                    return cost

        return len(link) * ord(link[0])


    def split_links(self,link, no_prefix_g_links, seperator):
        words = self.split_words(link, seperator)

        for w in range(1, len(words) - 1):
            if seperator.join(words[w:]) in no_prefix_g_links:
                if link in self.matched:
                    return 1005
                else:
                    self.matched.append(link)
                    return 5

        for w in range(len(words) - 1, 0, -1):
            if seperator.join(words[:w]) in no_prefix_g_links:
                if link in self.matched:
                    return 1005
                else:
                    self.matched.append(link)
                    return 5

        return None

    def split_words(self, link, seperator):
        return link.split(seperator)

    def utilize_dijk(self, source, goal):
        path = [source]

        g_html = self.internet.get_page(goal)
        g_links = Parser.get_links_in_page(g_html)

        prefix = "/wiki/"
        no_prefix_g_links = []
        for g_link in g_links:
            no_prefix_g_links.append(g_link[len(prefix):].lower())

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

                weight = self.calculateCost(neighbour, g_html, no_prefix_g_links)

                if neighbour in self.visited:
                    continue

                newCost = nodeCosts[current] + weight

                if neighbour == goal:
                    return shortest_path + [goal]

                if nodeCosts[neighbour] is None or nodeCosts[neighbour] > newCost:
                    nodeCosts[neighbour] = newCost
                    heap.heappush(pq, (newCost, neighbour, shortest_path + [neighbour]))
        return None


    def bidirectional_bfs(self, source, goal, direction="forward"):

        path = [source]
        forward_queue = []
        backward_queue = []
        forward_visited = []
        backward_visited = []

        forward_nodeCosts = defaultdict(lambda: float('inf'))
        forward_nodeCosts[source] = 0

        backward_nodeCosts = defaultdict(lambda: float('inf'))
        backward_nodeCosts[goal] = 0

        if source == goal:
            self.internet.get_page(source)
            return path + [goal]

        # forward_queue.append((source, [source]))
        # backward_queue.append((goal, [goal]))

        heap.heappush(forward_queue, (0, source, [source]))
        heap.heappush(backward_queue, (0, goal, [goal]))

        while forward_queue and backward_queue:

            _, f_page, f_shortest_path = heap.heappop(forward_queue)
            f_html = self.internet.get_page(f_page)
            f_links = Parser.get_links_in_page(f_html)
            forward_visited.append(f_page)

            _, b_page, b_shortest_path = heap.heappop(backward_queue)
            b_html = self.internet.get_page(b_page)
            b_links = Parser.get_links_in_page(b_html)
            backward_visited.append(b_page)

            # if f_page != source and b_page != goal:
            #     res = next((link for link in f_links if link in b_links), None)
            #
            #     if res:
            #         return f_shortest_path + [res] + b_shortest_path

            for f_link in f_links:
                forward_weight = self.calculateCost(f_page, b_html)
                if f_link in self.visited:
                    continue
                if f_link == goal:
                    # forward_queue.append((goal,f_shortest_path + [goal]))
                    return f_shortest_path + [goal]
                f_newCost = forward_nodeCosts[f_link] + forward_weight
                if forward_nodeCosts[f_link] is None or forward_nodeCosts[f_link] > f_newCost:
                    forward_nodeCosts[f_link] = f_newCost
                    heap.heappush(forward_queue, (f_newCost, (f_link, f_shortest_path + [f_link])))

            for b_link in b_links:
                backward_weight = self.calculateCost(b_page, f_html)

                if b_link in self.visited:
                    continue

                if b_link == source:
                    # backward_visited.append(goal)
                    return b_shortest_path + [goal]
                if b_link not in backward_visited:
                    backward_queue.append((b_link, [b_link] + b_shortest_path))

                b_newCost = backward_nodeCosts[b_link] + backward_weight

                if backward_nodeCosts[b_link] > b_newCost:
                    backward_nodeCosts[b_link] = b_newCost
                    heap.heappush(backward_queue, (b_newCost, b_link, [b_link] + b_shortest_path))

        return None


# KARMA
class FindInPageProblem:
    def __init__(self):
        self.internet = Internet()
        self.visited = []

    # This Karma problem is a little different. In this, we give you a source page, and then ask you to make up some heuristics that will allow you to efficiently
    #  find a page containing all of the words in `query`. Again, optimize for the fewest number of internet downloads, not for the shortest path.

    def find_in_page(self, source="/wiki/Calvin_Li", query=["ham", "cheese"]):

        path = []

        stack = []
        stack.append(source)

        while len(stack) > 0:
            found_lst = []
            top = stack.pop()
            self.visited.append(top)
            path.append(top)
            html = self.internet.get_page(top)
            links = Parser.get_links_in_page(html)
            for word in query:
                if re.search(r"\b" + re.escape(word) + r"\b", html):
                    found_lst.append(word)

                if word in links:
                    stack.append(link)

            if len(found_lst) == len(query):
                return path
            #             else:
            #                 path.pop()

            if len(stack) == 0:
                for link in links:
                    if link not in self.visited:
                        stack.append(link)
                        break
        return None


        # find a path to a page that contains ALL of the words in query in any place within the page
        # path[-1] should be the page that fulfills the query.
        # YOUR CODE HERE

        return path  # if no path exists, return None
