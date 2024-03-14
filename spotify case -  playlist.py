# %%
with open('Client_Spotify.txt', 'r') as file:
    ClientID=file.readline().strip()
    ClientSECRET=file.readline().strip()

# %%
import base64
import requests
import json
import pandas as pd
import os
import webbrowser
import spotipy.util as util

# %%
def get_token():
    auth_string = ClientID + ":" + ClientSECRET
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {"grant_type": "client_credentials"}                     #ACESSANDO O TOKEN DE AUTENTICAÇÃO
    result = requests.post(url, headers =headers, data=data)
    json_result = json.loads(result.content)
    print(json_result)
    
    token = json_result["access_token"]
    return token

token= get_token()

# %%
def get_auth_header(token):
    return {"Authorization": "Bearer " + token} #GERANDO AUTENTICAÇÃO

# %%
def get_playlist(token):
    playlist_url = "https://api.spotify.com/v1/playlists/3CCGunmspJS4J49EVRZhKJ/tracks"   #ACESSANDO A API PARA PEGAR A PLAYLIST
    headers = get_auth_header(token)
    response = requests.get(url=playlist_url, headers=headers)
    response.status_code

    return response.json()

playlist = get_playlist(token)

# %%
def get_genres(token,id):
    artist_url="https://api.spotify.com/v1/artists/{}".format(id) #ACESSANDO A API PARA PEGAR OS GÊNEROS DE CADA ARTISTA
    headers=get_auth_header(token)
    response = requests.get(url=artist_url, headers=headers)
    response.status_code
    
    return response.json()


# %%
track_completes=[]


for track in playlist['items']:
    track_info = track['track']
    track_name = track_info['name']
    inside_artist = track_info['artists']
    track_artists = ', '.join([artist['name'] for artist in inside_artist]) #CRIANDO O DATA FRAME
    track_album = track_info['album']['name']
    track_duration = round(((track_info['duration_ms'])*0.001)/60.0,2) #Transformando de milisegundo para minuto
    for artist in track_info['artists']: #TRAZENDO O GÊNERO PARA CADA ARTISTA MENCIONADO NA PLAYLIST
        genres = get_genres(token, artist['id'])
        genres=genres['genres']                      
        #print(genres)
    artist_id = track_info['id']
    track_pop = track_info['popularity']
    track_completes.append([track_name, track_artists,track_album,track_duration,track_pop, genres])
    
    


df=pd.DataFrame(track_completes, columns = ["Nome música", "Artista", "Album","Duração","Popularidade","Gênero"])

# %%
negrito = '\033[1m'
print(f"{negrito}Tamanho da playlist é de",len(df["Nome música"]),"músicas")

# %%
def generate_unique(type):
    type_total = type.str.split(',', expand=True) #separando os artistas/generos que tem mais de um por música
    #type_total.describe()
    type_unique = pd.concat([type_total[0],type_total[1],type_total[2],type_total[3]],axis=0,ignore_index=True) #concatenando tudo em uma coluna só

    return type_unique.unique() #Todos os artistas/generos na minha playlist

# %%
artists_unique = generate_unique(df["Artista"])
print(artists_unique) #LISTA ÚNICA DOS ARTISTAS NA PLAYLIST


# %%
negrito = '\033[1m'
print(f"{negrito}São",len(artists_unique),"artistas diferentes na playlist")

# %%
str_genres =', '.join(map(str, df["Gênero"])) #JUNTANDO RITMOS EM STRING SEPARADOS POR VÍRGULA
list_genres = []

for genreList in df["Gênero"].array:
    for genre in genreList:
        #genreList.append(genre)
        if genre not in list_genres: #GERANDO LISTA ÚNICA DE GÊNEROS
            list_genres.append(genre)
        
print(list_genres)

# %%
negrito = '\033[1m'
print(f"{negrito}São",len(list_genres),"tipos de gêneros diferentes na playlist")

# %%
df.describe()

# %%
def contagem(data_frame):              #ACUMULANDO CONTAGEM
    return data_frame.value_counts()

alb_counts=contagem(df["Album"]) #ACUMULANDO CONTAGEM PARA CADA ALBUM
art_counts=contagem(df["Artista"]) #ACUMULANDO CONTAGEM PARA CADA ARTISTA
gen_counts=contagem(df["Gênero"]) #ACUMULANDO CONTAGEM PARA CADA GÊNERO

# %%
gen_counts.plot.pie(label="")

# %%
threshold=3
valid_genres=gen_counts[gen_counts>threshold].index  #FILTRANDO PELAS OCORRÊNCIAS MAIORES DO QUE 3 PARA CADA GÊNERO, PARA OTIMIZAR O GRÁFICO
filter_gen = df[df["Gênero"].isin(valid_genres)]
gen_counts=filter_gen["Gênero"].value_counts()
gen_counts.plot(kind="pie",label="")

# %%
print(art_counts)

# %%
art_counts.plot.pie() #GRÁFICO DOS ARTISTAS SEM TRATAMENTO

# %%
threshold=2
valid_artists=art_counts[art_counts>=threshold].index  #FILTRANDO PELAS OCORRÊNCIAS MAIORES OU IGUAIS A 2 PARA CADA ARTISTA, PARA OTIMIZAR O GRÁFICO
filter_artist = df[df["Artista"].isin(valid_artists)]
art_counts=filter_artist["Artista"].value_counts()
art_counts.plot(kind="pie",label="")

# %%
alb_counts.plot.pie(label="") #GRÁFICO FICA MUITO POLUÍDO E MUITO DIFÍCIL DE VISUALIZAR

# %%
threshold=2
valid_alb=alb_counts[alb_counts>=threshold].index  #FILTRANDO PELAS OCORRÊNCIAS MAIORES OU IGUAIS A 2 PARA CADA ALBUM, PARA OTIMIZAR O GRÁFICO
filter_alb = df[df["Album"].isin(valid_alb)]
alb_counts=filter_alb["Album"].value_counts()
alb_counts.plot(kind="pie",label="")


