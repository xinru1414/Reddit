import os
import time
from collections import Counter
from datetime import date

import config
import pandas as pd
from typing import List, Dict
from reddit import Reddit


class TimelineSentence:
    number: int  # the index of the sentence in the post
    text: str  # The text of the sentence
    topic: str  # The id of the topic this sentence was assigned to

    def __init__(self, number, text, topic):
        self.number = number
        self.text = text
        self.topic = topic

    def __repr__(self):
        return f'Sentence #{self.number}\tTopic: {self.topic}\tText: "{self.text}"'


class TimelinePost:
    id: str  # Reddit id of post
    timestamp: int  # the unix time the post was posted
    sentences: List[TimelineSentence]

    def __init__(self, id, timestamp):
        self.id = id
        self.timestamp = timestamp
        self.sentences = []

    def __repr__(self):
        return f'Post "{self.id}" from "{time.ctime(self.timestamp)}"\n\t' + '\n\t'.join(map(repr, self.sentences))

    @property
    def year(self):
        ts = date.fromtimestamp(self.timestamp)
        return f'{ts.year}'

    @property
    def year_month(self):
        ts = date.fromtimestamp(self.timestamp)
        return f'{ts.year}-{ts.month}'


class AuthorTimeline:
    author: str
    posts: List[TimelinePost]

    def __init__(self, author, posts):
        self.author = author
        self.posts = posts

    def __repr__(self):
        return f'Timeline for "{self.author}"\n' + '\n'.join(map(repr, self.posts)) + '\n\n'

    def get_most_popular_month_timeline(self):
        counts = Counter(post.year_month for post in self.posts)

        if not counts:
            return AuthorTimeline(self.author, [])
        popular_month, _ = counts.most_common(1)[0]

        return self.get_posts_for_year_month(popular_month)

    def get_posts_for_year(self, year: str):
        return AuthorTimeline(self.author, list(filter(lambda x: x.year == year, self.posts)))

    def get_posts_for_year_month(self, year_month: str):
        """
        :param year_month: in the form "2018-03"
        """
        return AuthorTimeline(self.author, list(filter(lambda x: x.year_month == year_month, self.posts)))

    @property
    def sentence_texts(self):
        return [sent.text for post in self.posts for sent in post.sentences]

class TopicsDFCache:
    CACHE = {}

    @staticmethod
    def load(topic) -> pd.DataFrame:
        if topic not in TopicsDFCache.CACHE:
            #print(os.path.join(config.topic_dir, f'{topic}.csv'))
            df = pd.read_csv(os.path.join(config.topic_dir, f'{topic}.csv'))

            TopicsDFCache.CACHE[topic] = df
        return TopicsDFCache.CACHE[topic]


def get_authors_timeline(author: str, topics: List[str]) -> AuthorTimeline:
    reddit = Reddit(config.data_location)
    posts: Dict[str, TimelinePost] = {}

    for topic in topics:
        df = TopicsDFCache.load(topic)
        filtered_df = df[(df.Author == author)]
        for _, row in filtered_df.iterrows():
            post_id = row['SeqId']
            sentence_number = row['InstNo']
            text = row['Text']
            sent = TimelineSentence(sentence_number, text, topic)
            if post_id not in posts:
                create_time = reddit.get_post(post_id)['created_utc']
                posts[post_id] = TimelinePost(post_id, create_time)
            posts[post_id].sentences = list(sorted(posts[post_id].sentences + [sent], key=lambda x: x.number))

    sorted_posts = list(sorted(posts.values(), key=lambda x: x.timestamp))

    # selected_posts = list()
    #
    # year_dict = {2012:0,2013:0,2014:0,2015:0,2016:0,2017:0,2018:0}
    # month_dict = {1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,10:0,11:0,12:0}
    #
    # for item in sorted_posts:
    #     if date.fromtimestamp(item.timestamp).year in year_dict.keys():
    #         year_dict[date.fromtimestamp(item.timestamp).year] += 1
    # year = max(year_dict.items(), key=operator.itemgetter(1))[0]
    # for item in sorted_posts:
    #     if date.fromtimestamp(item.timestamp).year == year:
    #         if date.fromtimestamp(item.timestamp).month in month_dict.keys():
    #             month_dict[date.fromtimestamp(item.timestamp).month] += 1
    # month = max(month_dict.items(),key=operator.itemgetter(1))[0]
    #
    # for item in sorted_posts:
    #     if date.fromtimestamp(item.timestamp).year==year and date.fromtimestamp(item.timestamp).month==month
    #             selected_posts.append(item.sentences)

    # print(f'{author} most frequent year {year} and month {month}')
    return AuthorTimeline(author, sorted_posts)


if __name__ == '__main__':
    l1 = ['--Vespertine--', 'BreadCrumbles', 'HelloKimi', 'IANALbutIAMAcat', 'Khalibre', 'Letshavedinner2', 'MichellePoetta', 'Satellite0fLove', 'StrawberryGuillotine', 'TheVeggieLife', 'ThreeArmSally', 'Vanityisundead', 'YoungMetroTrustsYou', 'aliceblack', 'aloneh95', 'ashley_morrow', 'aspiesinger', 'baejaan', 'bdaly123', 'benoit_balls', 'birdonthewire', 'bluecowboyboots2', 'bronnygman', 'bulbysoar', 'cmVkZGl0', 'cortita', 'dlandwirth', 'eaudeboeuf', 'emtsevilla', 'giggles-mcgee', 'hot_tamale', 'i_wantthat', 'ileikboopy', 'islen', 'jeeed', 'karrmageddon', 'knitandpolish', 'labretkitty', 'laughingbabies', 'lillakatt', 'mathannamatics', 'moold', 'nattweeter', 'nelehx', 'nonspecificname', 'notaroundthehouse', 'obstreperosity', 'octopop', 'omgicantgetausername', 'orangemonkeyguy', 'pandadere', 'plasmaz', 'potmeetsthekettle', 'pvreppin', 'raymielle', 'roboeyes', 'sexymuscles-', 'sgartistry', 'spotty-belly', 'theriverstyxnstones', 'theycallmena', 'toogoodforthehut', 'xcdp10', 'yllwbrd']
    l2 = ['CineCine', 'Holaitscarlos', 'JumbledPileOfPerson', 'MyWayOrFuckU', 'Npatty90', 'SLYR', 'SianM10', 'SpuriousSpunk', 'Stony1234', 'Sylthar', '_cassquatch', 'acciointernet', 'boooooored', 'cassieness', 'chemistrygeek4eva', 'chinchillin88', 'contoddulations', 'crabstix11', 'cuhcuhcourtney', 'ddeevv', 'elektrodap', 'fatlittleparasite', 'filthyhookerpirate', 'gummar', 'halbarry', 'ieatstickers', 'jdeezy506', 'kebabmybob', 'knocking_', 'laurencat', 'lesmisfan12', 'linderpreet', 'lorelark', 'meowgrrr', 'mich1331', 'millenialwoman', 'nailsrglue', 'neslynn', 'om4mondays', 'overpaidbabysitter', 'pards1234', 'pink-melon', 'roarker', 'rvnaway', 'thehostilehobo', 'tiffanylove2', 'whatisdinero', 'yoochunsa']
    l3 = ['Mylsk', 'akreo', 'bonkstick', 'chasingandbelieving', 'matchakitkat', 'nakednark']
    l4 = ['AppleEverything', 'stirkee', 'wingardium_levibrosa']
    l6 = ['-BLLB-', '19751975', '26bonjourpapillon', 'AMElolzz', 'Amirwinn', 'Awfully_Nice', 'BMacintosh984', 'BavidDrent', 'Cathwoman21', 'ClassySlacks', 'CutiePanzer', 'DKT2001', 'DoctorQuinlan', 'Encie', 'GeeEmPee', 'HollaDude', 'IDontLikeLollipops', 'I_Heart_Squids', 'ImJello', 'Iroshizuku', 'Jadefury', 'JenniferHewitt', 'JurassicVibes', 'Kacers', 'Kalldaro', 'Kate22192', 'Kc1319310', 'KeepYourClawsOut', 'Laur-Ent', 'Lola1479', 'Lucy_Shinto', 'LunaSunshines', 'Melancholy96', 'Mercedene_Morghon', 'Morphiadz', 'MsQuince', 'P3rkoz', 'PinkestPeach', 'PiratesARGH', 'Purple-Leopard', 'Quolli', 'Rapsberry', 'RepostTony', 'RussianAsshole', 'SaveThe0xfordComma', 'Secretlysidhe', 'Sejura', 'Sleepyrabbitz', 'Slorebunny', 'Spectacularviewss', 'TPYogi', 'Tennislife', 'ThePlushest-', 'The_BusterKeaton', 'Thranrond', 'Whimsy515', 'Zweisoldner', 'ace463', 'acnecarethrowaway', 'acnedryskinsadness', 'alyaaz', 'anitahoiland', 'becca92079', 'bee27', 'bigbreathein24', 'bluesky557', 'cherryphoenix', 'dasoktopus', 'dcdc06', 'dee62383', 'diana_mt', 'dinosaur-pudge', 'drynesss', 'earth-wind-fire', 'eclats21', 'eisenkatze', 'eka5245', 'epi_mom', 'forsythiasilvia', 'frankiecool', 'franklintheknot', 'fsutan', 'fulopf', 'girlwithaspirin', 'guinnypig', 'guppyd', 'happychipmunkcheeks', 'heart_eyes_emoji', 'iendandubegin', 'ifindicanthide', 'iivyy', 'imdirtysocks45', 'inatorr', 'inc0nceivable', 'itsmyotherface', 'jakeylime', 'jnn-11000', 'jonilui', 'juicyfizz', 'justfordafunkofit', 'justsayno2carbs', 'kahiggins84', 'kenanthepro', 'kisses_turtles', 'littlebitty', 'lmg2br', 'lolaleee', 'long_term_catbus', 'lqcnyc', 'makeupmama33', 'marmosetohmarmoset', 'misandry4lyf', 'missbedlam', 'mmsryummy937', 'ninebubblewaters', 'offbrandsoap', 'ohhiitssteph', 'phamily_fotos', 'piratesandcash', 'port11', 'portisslave', 'qtUnicorn', 'reducky4me', 'salty-lemons', 'scale6', 'skinqq', 'standrightwalkleft', 'thaliaaa0', 'thankshermoninny', 'thebabes2', 'thecatspajaamas', 'thejavascripts', 'theman557', 'ticklystarlight', 'toxik0n', 'weddinggirl2015', 'wiirenet', 'winstonsmithluvsbb', 'xXVoicesXx', 'xotori', 'yoshisapple', 'yourmintmajesty']
    l5 = ['Burgermiester', 'DarkDubzs', 'MrsFart', 'NoctilucentSkies', 'Oh0k', 'RainyLeaves', 'TedBundyTeeth', 'ThatSkincareGuy', 'Tsmverymuch', 'Yes-Sarasly', 'bonghits4jess', 'cole780', 'daisyheartsvw', 'daisylion3', 'danaofdoom', 'dawn855', 'ddddamn', 'iamafoxiamafox', 'kinglourenco', 'kitti_mau', 'kittiemeow23', 'koukla1994', 'ladylala9', 'le_sweetie_man', 'mmencius', 'roll19ftw', 'starryeyedq', 'std5050', 'surlyskin', 'swallesque', 'tofutits', 'tracytracy22', 'ultrakawaii', 'urdyrr', 'wondawfully', 'xsp4rrow']

    l7 = ['jamessnow', 'TheSov', 'gordonmcdowell', 'BeezleyBillyBub', 'TheLegionsOfHell', 'Yuli-Ban', 'BeezelyBillyBub', 'nebulousmenace', 'Gmanacus', 'terp_nolan']
    l8 = ['VegetarianPerson', 'Kelly-Logan', 'pkrhed', 'assousa', 'JRugman', 'DrFreemanDyson', 'ChingShih', 'zvra210', 'WhaTheWhy', 'RLM_']
    l9 = ['eclipsenow', 'philthechemist', 'ElectricRebel', 'allquixotic', 'BAS_Energy', 'wrath0110', 'TheKingOfCryo', 'iowajaycee', 'SnowGN', 'xrm67']

    l10 = ['RLM_', 'ChingShih', 'WhaTheWhy', 'allquixotic', 'unsoldmerchant', 'xrm67', 'zvra210', 'gnikivar2', 'ElectricRebel', 'zanaks']
    l11 = ['afrobat', 'jamessnow', 'villadsknudsen', 'Yuli-Ban', 'TheSov', 'terp_nolan', 'DonManuel', 'bikermonk', 'TheLegionsOfHell', 'fastj83']

    l_all_0 = ['communityDOTsolar', 'dmguion', 'calmblueocean']
    l_all_1 = ['BelovedLady', 'MayKingKar', 'HeartofAthena']
    l_all_2 = ['ceramicfiver', 'shoptxelectricity', 'georedd']

    l_all_state_0 = ['CommonEmployment', 'SevereAnxiety76', 'communityDOTsolar', 'forWatermen', 'kill_pussycat', 'l0ther', 'lawrencewidman', 'maryhadalittlelbomb', 'unsynched']
    l_all_state_1 = ['HRGreen', 'ILikeNeurons']
    l_all_state_2 = ['ceramicfiver', 'obsidian468']

    for item in l_all_state_2:
        print(get_authors_timeline(item, ['FT1', 'FT3', 'FT6', 'FT8']))



