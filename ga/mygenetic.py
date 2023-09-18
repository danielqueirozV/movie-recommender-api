
from ga.algorithm import Algorithm
from sqlalchemy.orm import Session
from fastapi import Depends
import numpy as np
import math 

from db.database import get_db
from db.repositories import UserRepository, MovieRepository, RatingsRepository

class MyGeneticAlgorithm(Algorithm):

    def __init__(self, query_search, individual_size, population_size, p_crossover, p_mutation, all_ids, max_generations=100, size_hall_of_fame=1, fitness_weights=(1.0, ), seed=42, db=None) -> None:


        super().__init__(
            individual_size, 
            population_size, 
            p_crossover, 
            p_mutation, 
            all_ids, 
            max_generations, 
            size_hall_of_fame, 
            fitness_weights, 
            seed)
        
        self.db = db
        self.all_ids = all_ids
        self.query_search = query_search
        

    
    def pesoUser(self):
        user = self.query_search
        listaNotas = RatingsRepository.find_by_userid(self.db, user)
        
        peso = {
            "Action": 0,
            "Adventure": 0,
            "Animation": 0,
            "Children": 0,
            "Comedy": 0,
            "Crime": 0,
            "Documentary": 0,
            "Drama": 0,
            "Fantasy": 0,
            "Film-Noir": 0,
            "Horror": 0,
            "Musical": 0,
            "Mystery": 0,
            "Romance": 0,
            "Sci-Fi": 0,
            "Thriller": 0,
            "War": 0,
            "Western": 0,
            "(no genres listed)": 0
        }
        for nota in listaNotas:
                filme = MovieRepository.find_by_id(self.db, nota.movieId)
                for genero in filme.genres.split("|"):
                    if genero in peso: 
                        peso[genero] += nota.rating

        return peso

    
    def individualevaluate(self, lista,filme, peso):
        
        ratings = np.array(lista.rating)
        
        media_ratings = np.mean(ratings)
        generos = MovieRepository.find_by_id(self.db,filme).genres.split("|")
        
        soma_pesos = 0
        
        nota_ponderada = sum([media_ratings * peso.get(g, 0) for g in generos])
        soma_pesos += sum([peso.get(g,0) for g in generos if g in generos])
        
        if soma_pesos > 0:
            media_ponderada = nota_ponderada / soma_pesos
        else:
            media_ponderada = 0

        return media_ponderada



    def evaluate(self, individual):

        if len(individual) != len(set(individual)):
            return (0.0, )
        
        if len(list(set(individual) - set(self.all_ids))) > 0:
            return (0.0, )
        
        medias = []
        peso = self.pesoUser()
        ratings_movies = RatingsRepository.find_by_movieid_list(self.db, individual)
        

        if len(ratings_movies) > 0:
            for nota in ratings_movies:
                nota = self.individualevaluate(nota,nota.movieId, peso)
                medias.append(nota)
            mean_ = np.mean(medias)
        else:
            mean_ = 0.0

        return (mean_, )

