import matplotlib.pyplot as plt
import numpy as np
import cv2
from itertools import chain
from scipy import ndimage
import re
import math
import pandas
import csv


BRANCO = 255
vizinhos = [[0,0],[0,-1],[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1]]

def bool_nas_Fronteiras(ponto, listaDeFronteiras):
    for f in listaDeFronteiras:
        if boolPontoNaBorda(ponto, f):
            return True
    return False

def encontrar_prox_branco(ponto, img):
    i, j = ponto
    row, col = img.shape
    while(i<row):
        while (j<col):
            if img[i,j] >= BRANCO:
               return(i,j)     
            j+=1
        j=0        
        i+=1
    return (i-1,j)

def find_next_point(img, last_pixel, listaDeFronteiras):
    i, j = last_pixel
    row, col = img.shape
    i+=1
    while(i<row):
        while (j<col):
            if img[i,j] < BRANCO and img[i, j-1] >= BRANCO:
                if bool_nas_Fronteiras((i,j), listaDeFronteiras) == False: #retorna o ponto
                    return (i,j)
                else:#percorre a imagem ate achar um branco
                    ponto_branco = encontrar_prox_branco((i,j), img)
                    i=ponto_branco[0]
                    j=ponto_branco[1]
                    continue
            j+=1
        j=0        
        i+=1
    return 0

def boolPontoNaBorda(ponto, fronteira):
    return ponto in fronteira #encontrou o primeiro pronto da lista de fronteira

def find_no_white(img):
    row, col = img.shape        
    for i in range(row):
        for j in range(col):
            if img[i,j] < BRANCO:
                return (i,j)

def obterVizinhoID(x, y): 
    for i in range(9):
        if(x == vizinhos[i][0] and y == vizinhos[i][1]):
            return i            

def seguidorDeFronteira(img, first_pixel, i):
    row, col = img.shape        
    fronteira=[]
    fronteira.append(first_pixel)
    x = 0
    y = 1 #intuito de deixar o código mais legível
    
    b_0 = [first_pixel[x], first_pixel[y]] #b_0[0] = x , b_0[1] = y
    c_0 = [0, -1]
    anterior_b0 = [0, 0]
    cont = 1
    contador_de_vizinhos = 0
    find_init_border = True
    contador=0
    while(find_init_border):
        indexVizinho=obterVizinhoID(c_0[x], c_0[y]) 
        while(True):

            if(indexVizinho == 8):#zerar o clock
                indexVizinho = 0   
            
            proxB_0 = [b_0[x]+vizinhos[indexVizinho+1][x], b_0[y]+vizinhos[indexVizinho+1][y]]
            proxVizinho = [b_0[x]+vizinhos[indexVizinho+1][x], b_0[y]+vizinhos[indexVizinho+1][y]] #atualiza para o próximo vizinho

            if (img[proxVizinho[x]][proxVizinho[y]]<BRANCO) and cont==0: #verifica se o próximo vizinho é BRANCO
                b_0 = [proxB_0[x], proxB_0[y]]                       
                check = (b_0[x],b_0[y])    
                #if boolPontoNaBorda(check, fronteira) and len(fronteira)>550: #encontrou o primeiro pronto da lista de fronteira
                #if boolPontoNaBorda(check, fronteira): #encontrou o primeiro pronto da lista de fronteira
                if (first_pixel == check):
                    find_init_border = False
                    break
                else:    
                    fronteira.append((b_0[x],b_0[y]))
                c_0 = [anterior_b0[x]-b_0[x], anterior_b0[y]-b_0[y]]
                contador_de_vizinhos = 0
                contador+=1
                if proxB_0[x] > row: #para quando sair da imagem
                    return False, (0,0)
                break
            contador_de_vizinhos +=1
            if contador_de_vizinhos == 9: #para quando estiver um loop infinito
                return False, (0,0)
            cont = 0
            anterior_b0 = [proxB_0[x], proxB_0[y]]
      
            indexVizinho += 1 
    
    tamanho = len(fronteira)
    if tamanho>50 and tamanho<25000:
        return True, fronteira

    return False, (0,0)

def grayscale(img):
    vetor_pixels = []
    k=0
    row, col, bpp = np.shape(img)

    for i in range(0,row):
        for j in range(0,col):
            b = int(img[i][j][0])
            g = int(img[i][j][1])
            r = int(img[i][j][2])
            pixel = int((b+g+r) / 3)  
            vetor_pixels.append(pixel)

    for i in range(0,row):
        for j in range(0,col):
            img[i][j][0] = float(vetor_pixels[k])
            img[i][j][1] = float(vetor_pixels[k])
            img[i][j][2] = float(vetor_pixels[k])
            k +=1 

    return img

def remove_ruidos(imagem):
    img = imagem.astype('float')
    img = img[:,:,0] # convert to 2D array
 
    gray_img = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    #gray_img = grayscale(imagem);
    
    _,img = cv2.threshold(gray_img, 225,255, cv2.THRESH_BINARY)
    img = cv2.medianBlur(img, 5)
    
    cv2.imwrite("saida1.png", gray_img)   
    cv2.imwrite("saida2.png", img)

    return img   

def init(img):
    #avg = np.mean(imagem,axis=-1)
    
    listaDeFronteiras=[]

    first_no_white_pixel = find_no_white(img)
    next_pixel = first_no_white_pixel
    i=0
    while(next_pixel!=0): 
        try:
            is_fronteira, fronteira = seguidorDeFronteira(img, next_pixel, i)
            tamanho_fronteira = len(fronteira)
            
            if is_fronteira:
                listaDeFronteiras.append(fronteira)
            
            last_pixel = next_pixel
            next_pixel =  find_next_point(img, last_pixel, listaDeFronteiras)
        except Exception as e:
            print(e)
        i+=1

    #este tratamento funciona devido a imagem 13 qual o background não é totalmente branco
    for front in listaDeFronteiras:
        if len(front) > 19000:
            listaDeFronteiras.remove(front)

    print("NUMERO DE FOLHAS ENCONTRADAS:")
    print(len(listaDeFronteiras))

    #contour = np.zeros((imagem.shape)) #cria uma matriz do tamanho da imagem preenchida com zero
    #for i in listaDeFronteiras:
    #    for pixel in range(len(i)):
    #        contour[i[pixel][0]][i[pixel][1]] = [255,255,255]
    

    #cv2.imshow('Image', imagem)
    #cv2.imshow('Image_contour', contour)
    #cv2.imwrite("saida.png", contour)   
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return listaDeFronteiras

def encontra_dimensoes(fronteira):
    x = 0
    y = 1

    list_y = [cord_y[y] for cord_y in fronteira]
    list_x = [cord_x[x] for cord_x in fronteira]

    x_menor = list_x[0] #pega a primeira posicao
    x_maior = max(list_x)
    y_menor = min(list_y) 
    y_maior = max(list_y)

    return (x_maior-x_menor)+3 , (y_maior-y_menor)+3, x_menor, y_menor, x_maior, y_maior


def criar_imagem_borda(img_borda, fronteira, menor_x, menor_y, index, name_img):
    #img_borda_binaria = np.zeros(img_borda.shape)
    row, col, bpp = img_borda.shape
    img_borda_binaria = np.zeros((row, col))
    
    for pixel in fronteira:
        nova_coordenada_x = (int(pixel[0])-menor_x)+1
        nova_coordenada_y = (int(pixel[1])-menor_y)+1

        img_borda[nova_coordenada_x][nova_coordenada_y][0] = 0
        img_borda[nova_coordenada_x][nova_coordenada_y][1] = 0
        img_borda[nova_coordenada_x][nova_coordenada_y][2] = 0

        #criando imagem binaria
        img_borda_binaria[nova_coordenada_x][nova_coordenada_y] = 1

    nome_imagem = name_img + '-' + str(index) +"-P"+ ".png"
    cv2.imwrite(nome_imagem, img_borda)


    img_borda_binaria = ndimage.binary_fill_holes(img_borda_binaria).astype(int)

    #nome_imagem_binaria = 'BordaB' + str(index) + ".png"
    #cv2.imwrite(nome_imagem_binaria, img_borda_binaria*255)

    return img_borda_binaria   


def getColor(pixel, imagem_original, pos_x, pos_y):
    RGB = []
    #pegar a posição do pixel na imagem
    #posicao_do_pixel = posicao_pixel(imagem_original, pixel)
    pos_x = pixel[0] + 1
    pos_y = pixel[1] + 1 

    return imagem_original[pos_x,pos_y], pos_x, pos_y



def criar_imagem_unica_folha_colorida(img, imagem_original, imagem_branca, fronteira, img_borda_binaria, index, menor_x, menor_y, name_img):
    row, col, bpp = np.shape(imagem_branca)

    for i in range(row):
        for j in range(col):
            if img_borda_binaria[i][j] == 1:
                nova_coordenada_x = i+menor_x+1
                nova_coordenada_y = j+menor_y+1

                imagem_branca[i][j][0] = imagem_original[nova_coordenada_x][nova_coordenada_y][0]
                imagem_branca[i][j][1] = imagem_original[nova_coordenada_x][nova_coordenada_y][1]
                imagem_branca[i][j][2] = imagem_original[nova_coordenada_x][nova_coordenada_y][2]



    nome_imagem = name_img + '-' + str(index) + ".png"
    cv2.imwrite(nome_imagem, imagem_branca)

    return imagem_branca   
            


def recorta_imagem(lista_fronteiras, imagem_sem_ruido, imagem_original, name_img):
    
    index = 1
    for fronteira in lista_fronteiras:
        row, col, menor_x, menor_y, maior_x, maior_y = encontra_dimensoes(fronteira)#encontar a largura e a altura 
        
        #salavando a borda
        imagem_branca = np.ones((row, col, 3)) * 255
        cv2.imwrite("Branco.png", imagem_branca)   
        
        img_borda_binaria = criar_imagem_borda(imagem_branca, fronteira, menor_x, menor_y, index, name_img)
        
        #salvando a folha
        criar_imagem_unica_folha_colorida(imagem_sem_ruido, imagem_original, imagem_branca, fronteira, img_borda_binaria, index, menor_x, menor_y, name_img)
        index += 1 
    

def valor_medio(histograma, lista_probabilidade):
    medio = 0
    j = 0
    for i in histograma:
        medio = medio + (histograma[i] * lista_probabilidade[j])
        j += 1

    return medio

def pixeis_coloridos(histograma):
    total = 0 
    for i in histograma:
        total += histograma[i]
    return total

def probabilidade_de_cada_cor(histograma):
    lista_probabilidade = []
    total_pixeis_coloridos = pixeis_coloridos(histograma)
    for i in histograma:
        probabilidade = histograma[i] / total_pixeis_coloridos
        lista_probabilidade.append(probabilidade)  

    return lista_probabilidade

def obter_histograma(imagem):
    row, col, bpp =  np.shape(imagem)
    histograma = {}

    for i in range(row):
        for j in range(col):
            cor = tuple(imagem[i][j].tolist())
            if np.mean(imagem[i][j]) != BRANCO:
                if cor in histograma.keys(): 
                    histograma[cor] +=1                 
                else:    
                    histograma[cor] = 1
    
    return histograma 

#função que retorna a media, variancia, uniformidade, entropia de cada folha
def analise_textura(name_img, img_number):
    name_img = name_img + '-' + str(img_number) + ".png"
    imagem = cv2.imread(name_img)

    histograma = obter_histograma(imagem)
    probabilidade = probabilidade_de_cada_cor(histograma)

    m = valor_medio(histograma, probabilidade)
    j = 0
    media = variancia = uniformidade = entropia = 0 
    for i in histograma:
        media += (((histograma[i]-m)**1) * probabilidade[j])
        variancia += (((histograma[i]-m)**2) * probabilidade[j])
        uniformidade += (probabilidade[j] ** 2)# * histograma [i])
        entropia += (probabilidade[j] * np.log2(probabilidade[j])) * -1
        j += 1
    
    #media, variancia = media_e_variancia(m, histograma, lista_probabilidade)
    #uniformidade = uniformidade_histograma(histograma, lista_probabilidade)
    #entropia = entropia_img(histograma, lista_probabilidade)
    #z é a do cor do pixel
    #m = valor medio de z
    #p = probabilidade 
    #z_i = é o pixel 
    #m = quantidade de vezes que a cor ocorreu * probabilidade da cor
    return media, variancia, uniformidade, entropia

def pegar_nome(img_number):
    name_img = 'Folhas/Teste'
    if(img_number < 10):
        name_img = name_img + '0' 
    name_img = name_img + str(img_number) + '.png'
    imagem = cv2.imread(name_img)
    name_img = name_img.split(".")[0]

    return imagem, name_img

def criar_planilha():
    planilha = csv.writer(open("SAIDAS.csv", "w"))
    planilha.writerow(["ID imagem", "ID folha", "Media", "Variancia", "Uniformidade", "Entropia", "Perimetro"])

    return planilha

def incrementar_planilha(planilha, id_img, id_folha, media, variancia, uniformidade, entropia, perimetro):
    id_img =  id_img.removeprefix('Folhas/')
    planilha.writerow([id_img, id_folha, media, variancia, uniformidade, entropia, perimetro])

def main():
    
    print("Bem Vindo ao Trabalho de BIDI")
    
    img_number = 1
    planilha = criar_planilha()    
    
    
    while(True): #arrumar este while não ESQUECER
        try:
            imagem, name_img = pegar_nome(img_number)
            img_sem_ruido = remove_ruidos(imagem)        
            lista_fronteiras = []
            lista_fronteiras = init(img_sem_ruido) #encontrar as bordas
            recorta_imagem(lista_fronteiras, img_sem_ruido, imagem, name_img) # recortar as folhas e salvar em disco (salvar a borda e a folha colorida)
            
            index_sub_folha =  1
            while True:
                try: 
                    media, variancia, uniformidade, entropia = analise_textura(name_img, index_sub_folha)
                    perimetro = len(lista_fronteiras[index_sub_folha-1])  
                    incrementar_planilha(planilha, name_img, index_sub_folha, media, variancia, uniformidade, entropia, perimetro)
                    index_sub_folha += 1
                except:
                    print("Fim da análise de textura para todas as folhas encontradas no arquivo: ", name_img)
                    break   
            img_number += 1
        except:
            print("Finalmente acabou :) EBAA!")
            break

    

if __name__ == "__main__":
    main()