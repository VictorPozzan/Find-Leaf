import numpy as np
import cv2
from scipy import ndimage
import math
import csv

BRANCO = 255
vizinhos = [[0,0],[0,-1],[-1,-1],[-1,0],[-1,1],[0,1],[1,1],[1,0],[1,-1]]

#verifica se o ponto pertence a uma fronteira
def bool_nas_Fronteiras(ponto, listaDeFronteiras):
    for f in listaDeFronteiras:
        if boolPontoNaBorda(ponto, f):
            return True
    return False

#retorna a posição de um pixel branco
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

#retorna o proximo ponto diferente de branco e que não esta na lista de fronteiras
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

#encontra o primeiro pixel diferente de branco
def find_no_white(img):
    row, col = img.shape        
    for i in range(row):
        for j in range(col):
            if img[i,j] < BRANCO:
                return (i,j)#retorna a posição do pixel

#retorna a posição do array vizinhos
def obterVizinhoID(x, y): 
    for i in range(9):
        if(x == vizinhos[i][0] and y == vizinhos[i][1]):
            return i            

#a partir de um pixel inicial percorre a borda da folha
def seguidorDeFronteira(img, first_pixel, i):
    row, col = img.shape        
    fronteira=[]
    fronteira.append(first_pixel) # adiciona o primeiro pixel já na lista de fronteira
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

                if (first_pixel == check): # quando encontrar o primeiro pixel novamente acaba o seguidor de fronteira
                    find_init_border = False
                    break
                else:    
                    fronteira.append((b_0[x],b_0[y])) # adiciona na lista de fronteiras
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
      
            indexVizinho += 1 #incrementa o vizinho
    
    tamanho = len(fronteira)
    if tamanho>50 and tamanho<25000: #tratamento da imagem 13 
        return True, fronteira

    return False, (0,0)

def grayscale(img):
    row, col, bpp = np.shape(img)
    img_gray = []

    for i in range(0,row):
        for j in range(0,col):
            b = int(img[i][j][0])
            g = int(img[i][j][1])
            r = int(img[i][j][2])
            pixel = int((b+g+r) / 3)   
            img_gray.append(pixel) 
 
    return img_gray

def remove_ruidos(imagem):
    img = imagem.astype('float')
    img = img[:,:,0] # convert to 2D array
 
    gray_img = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY) #converte para tom de cinza
    
    _,img = cv2.threshold(gray_img, 225,255, cv2.THRESH_BINARY) #converte para binario
    img = cv2.medianBlur(img, 5) # remove o ruido 

    return img   

#inicio do algoritmo seguidor de fronteiras
def init(img):
  
    listaDeFronteiras=[]

    first_no_white_pixel = find_no_white(img)
    next_pixel = first_no_white_pixel
    i=0
    while(next_pixel!=0): 
        try:
            is_fronteira, fronteira = seguidorDeFronteira(img, next_pixel, i)
            
            if is_fronteira: #caso seja uma fronteira valida
                listaDeFronteiras.append(fronteira)
            
            last_pixel = next_pixel
            next_pixel =  find_next_point(img, last_pixel, listaDeFronteiras)
        except Exception as e:
            print(e)
        i+=1

    #este tratamento funciona devido a imagem 13 
    for front in listaDeFronteiras:
        if len(front) > 19000:
            listaDeFronteiras.remove(front)

    print("NUMERO DE FOLHAS ENCONTRADAS:")
    print(len(listaDeFronteiras))

    return listaDeFronteiras

#retorna a altura, largura, menor linha e menor coluna 
def encontra_dimensoes(fronteira):
    x = 0
    y = 1

    list_y = [cord_y[y] for cord_y in fronteira]
    list_x = [cord_x[x] for cord_x in fronteira]

    x_menor = list_x[0] #pega a primeira posicao
    x_maior = max(list_x)
    y_menor = min(list_y) 
    y_maior = max(list_y)

    #+3 serve para adicionar uma borda branca
    return (x_maior-x_menor)+3 , (y_maior-y_menor)+3, x_menor, y_menor

#cria a imagem da fronteira e retorna uma imagem com a mascara
def criar_imagem_borda(img_borda, fronteira, menor_x, menor_y, index, name_img):
    row, col, bpp = img_borda.shape
    img_borda_binaria = np.zeros((row, col))
    
    for pixel in fronteira: #transalada os pixeis
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


    return img_borda_binaria   

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
        row, col, menor_x, menor_y = encontra_dimensoes(fronteira)
        
        #salavando a borda
        imagem_branca = np.ones((row, col, 3)) * 255        
        img_borda_binaria = criar_imagem_borda(imagem_branca, fronteira, menor_x, menor_y, index, name_img)
        
        #salvando a folha
        criar_imagem_unica_folha_colorida(imagem_sem_ruido, imagem_original, imagem_branca, fronteira, img_borda_binaria, index, menor_x, menor_y, name_img)
        index += 1 
    
def valor_medio(histograma, lista_probabilidade):
    media = 0
    j = 0
    for i in histograma:
        media += i * lista_probabilidade[j]
        j += 1

    return media

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
    histograma = {}
    img_gray = grayscale(imagem) #converte para tons de cinza arrendondando o valor 

    for cor in img_gray:
        if cor != BRANCO:    
            if cor in histograma.keys():
                histograma[cor] += 1
            else:  
                histograma[cor] = 1
    
    return histograma 

#função que retorna a media, variancia, uniformidade, entropia de cada folha
def analise_textura(name_img, img_number):
    name_img = name_img + '-' + str(img_number) + ".png"
    imagem = cv2.imread(name_img)

    histograma = obter_histograma(imagem)
    probabilidade = probabilidade_de_cada_cor(histograma)

    media = valor_medio(histograma, probabilidade)
    j = 0
    variancia = uniformidade = entropia = 0 
    for i in histograma:     
        variancia += (((i-media)**2) * probabilidade[j])
        uniformidade += (probabilidade[j] ** 2)
        entropia += (probabilidade[j] * np.log2(probabilidade[j])) * -1
        j += 1
    
    return media, variancia, uniformidade, entropia

#realiza o tratamento do nome da imagem 1 -> Teste01 retorna o nome e a imagem do disco
def pegar_nome(img_number):
    name_img = 'Folhas/Teste'
    if(img_number < 10):
        name_img = name_img + '0' 
    name_img = name_img + str(img_number) + '.png'
    imagem = cv2.imread(name_img)
    name_img = name_img.split(".")[0]

    return imagem, name_img

#cria a planilha .csv e adiciona os cabeçalhos
def criar_planilha():
    planilha = csv.writer(open("SAIDAS.csv", "w"))
    planilha.writerow(["ID imagem", "ID folha", "Media", "Variancia", "Uniformidade", "Entropia", "Perimetro"])

    return planilha

#escreve na planilha os dados obtidos de cada folha
def incrementar_planilha(planilha, id_img, id_folha, media, variancia, uniformidade, entropia, perimetro):
    id_img =  id_img.removeprefix('Folhas/')
    planilha.writerow([id_img, id_folha, media, variancia, uniformidade, entropia, perimetro])

#função principal do código qual chama as funções de execução
def main():
    
    print("Bem Vindo ao Trabalho de PID")
    
    img_number = 1
    planilha = criar_planilha()    
    
    while(True): 
        try:
            imagem, name_img = pegar_nome(img_number)
            img_sem_ruido = remove_ruidos(imagem)        
            lista_fronteiras = []
            print("Encontrando todas as bordas de: ", name_img)
            print("     Este processo pode demorar um pouco")
            lista_fronteiras = init(img_sem_ruido) #encontrar as bordas
            recorta_imagem(lista_fronteiras, img_sem_ruido, imagem, name_img) # recortar as folhas e salvar em disco (salvar a borda e a folha colorida)
            print("Analisando a textura das folhas encontradas") 
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
            print("Acabou :) EBAA!")
            break

if __name__ == "__main__":
    main()

