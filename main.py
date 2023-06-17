import requests
from bs4 import BeautifulSoup


def get_actors(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    actors_list = soup.find_all('div', class_='lister-item-content')
    actors = [actor.find('h3').find('a').text.strip() for actor in actors_list]

    return actors

def get_actor_movies(actor_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }
    response = requests.get(actor_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    movie_list_selector = '#__next > main > div > section.ipc-page-background.ipc-page-background--base.sc-f9e7f53-0.ifXVtO > div > section > div > div.sc-243fb82e-2.kwKkbX.ipc-page-grid__item.ipc-page-grid__item--span-2 > div.celwidget > section:nth-child(2) > div:nth-child(5) > div.ipc-accordion.sc-5cecff0c-0.WeRzr.date-credits-accordion.ipc-accordion--base.ipc-accordion--dividers-none.ipc-accordion--pageSection > div > div.ipc-accordion__item__content > div > ul'

    movies_list = soup.select(f'{movie_list_selector} a.ipc-metadata-list-summary-item__t')
    movie_years = soup.select(f'{movie_list_selector} div.ipc-metadata-list-summary-item__cc > ul > li > span')
    movie_ids = [a['href'][7:] for a in movies_list]





    movies = []
    for movie, year, id  in zip(movies_list, movie_years, movie_ids):
        movie_name = movie.text.strip()
        movie_year = year.text.strip()
        movie_id = id
        movies.append((movie_name, movie_year, movie_id))

    return movies

def get_actor_awards(actor_url):
    awards_url = f"https://www.imdb.com{actor_url}/awards/?ref_=nm_ql_2"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }
    response = requests.get(awards_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    awards_list = soup.select('div.ipc-metadata-list-summary-item__c')

    awards = []
    for award in awards_list:
        award_name_element = award.find('a', class_='ipc-metadata-list-summary-item__t')
        award_year_element = award.find('ul', class_='ipc-inline-list')
        if award_name_element and award_year_element:
            award_name = award_name_element.text.strip()
            award_year = award_year_element.find('li').text.strip()
            awards.append((award_name, award_year))

    return awards
dsfoij

def get_actor_genre_from_movies(movies):
    genres = set()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }

    for _, _, movie_id in movies:

        movie_url = f"https://www.imdb.com/title/{movie_id}/?ref_=nm_flmg_t_12_act"



        response = requests.get(movie_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        genre_element = soup.find('span', class_='ipc-chip__text')
        if genre_element:
            genre = genre_element.text.strip()
            splitted_genres = genre.split(', ')
            for splitted_genre in splitted_genres:
                genres.add(splitted_genre)

    if genres:
        return ', '.join(genres)

    return None


def get_average_rating(movie_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36'
    }
    movie_url = f"https://www.imdb.com/title/{movie_id}/?ref_=nm_flmg_t_12_act"
    response = requests.get(movie_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    rating_element = soup.select_one('#__next main div section div:nth-child(4) section section div.sc-385ac629-3.kRUqXl div.sc-3a4309f8-0.fjtZsE.sc-52d569c6-1.knkDWf div div:nth-child(1) a span div div.sc-bde20123-0.gtEgaf div.sc-bde20123-2.gYgHoj span.sc-bde20123-1.iZlgcd')
    if rating_element:
        rating = rating_element.text.strip()
        return rating
    else:
        return None


def print_actor_info(actor, url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')


    actor_content = None
    for actor_div in soup.find_all('div', class_='lister-item-content'):
        if actor_div.find('h3').find('a').text.strip() == actor:
            actor_paragraphs = actor_div.find_all('p')
            if len(actor_paragraphs) > 1:
                actor_content = actor_paragraphs[1].text.strip()
            actor_bio_link = actor_div.find('h3').find('a')['href']
            full_bio_url = f"https://www.imdb.com{actor_bio_link}"
            break

    if actor_content is not None:
        print(f"--------------")
        print(f"Actor: {actor}")
        print(actor_content)
        print(f"Full Biography: {full_bio_url}")

        # Retrieve actor's movies from their individual IMDb page
        actor_movies = get_actor_movies(full_bio_url)

        if actor_movies:


            print(f"\nLatest Movies and Years for {actor}:")
            for i, (movie_name, movie_year, movie_id) in enumerate(actor_movies, 1):
                print(f"{i}. {movie_name} ({movie_year})")

            # Retrieve actor's genre from their movies
            # Inside the print_actor_info function

            actor_genre = get_actor_genre_from_movies(actor_movies)

            if actor_genre:
                print(f"\nGenre for {actor}: {actor_genre}")
            else:
                print(f"No genre information found for {actor}")

            print(f"For more movies, click {full_bio_url}")
        else:
            print(f"No movie information found for {actor}")

        # Retrieve actor's average rating for movies
        average_rating_overall = get_average_rating(movie_id)
        average_ratings_yearly = {}

        for _, movie_year, movie_id in actor_movies:
            average_rating_year = get_average_rating(movie_id)
            if average_rating_year:
                average_ratings_yearly[movie_year] = average_rating_year

        if average_rating_overall:
            print(f"\nAverage Rating for {actor}: {average_rating_overall}")
        else:
            print(f"No average rating information found for {actor}")

        if average_ratings_yearly:
            print("\nAverage Ratings by Year:")
            for year, rating in average_ratings_yearly.items():
                print(f"{year}: {rating}")

        # Retrieve actor's awards from their individual IMDb page
        actor_awards = get_actor_awards(actor_bio_link)

        if actor_awards:
            print(f"\nAwards for {actor}:")
            for award_name, award_year in actor_awards:
                if "Winner" in award_name:
                    print(f"{award_name} ({award_year})")
        else:
            print(f"No award information found for {actor}")
    else:
        print(f"Information not found for {actor}")


if __name__ == "__main__":

    imdb_url = "https://www.imdb.com/list/ls053501318/"
    actors = get_actors(imdb_url)

    # Print numbered list of actors
    for i, actor in enumerate(actors, 1):
     print(f"{i}. {actor}")

    # Prompt user for actor selection
    choice = input("Enter the actor number or name for more info (or 'q' to quit): ")
    while choice.lower() != 'q':
        if choice.isdigit() and int(choice) in range(1, len(actors) + 1):
            actor_index = int(choice) - 1
            selected_actor = actors[actor_index]
        elif choice in actors:
            selected_actor = choice
        else:
            print("Invalid input. Please enter a valid actor number or name.")
            choice = input("Enter the actor number or name for more info (or 'q' to quit): ")
            continue

        print_actor_info(selected_actor, imdb_url)

        choice = input("\nEnter the actor number or name for more info (or 'q' to quit): ")
