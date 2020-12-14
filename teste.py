import matplotlib.pyplot as plt
import numpy as np
import cv2
from itertools import chain

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
    print(i)
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
            print("iteracao: ", i)
            is_fronteira, fronteira = seguidorDeFronteira(img, next_pixel, i)
            tamanho_fronteira = len(fronteira)
            
            if is_fronteira:
                listaDeFronteiras.append(fronteira)
            
            last_pixel = next_pixel
            next_pixel =  find_next_point(img, last_pixel, listaDeFronteiras)
            print("tamanho da fronteira: ", tamanho_fronteira)
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

def criar_imagem_borda(img_borda, fronteira, menor_x, menor_y, index):

    for pixel in fronteira:
        nova_coordenada_x = (int(pixel[0])-menor_x)+1
        nova_coordenada_y = (int(pixel[1])-menor_y)+1

        img_borda[nova_coordenada_x][nova_coordenada_y][0] = 0
        img_borda[nova_coordenada_x][nova_coordenada_y][1] = 0
        img_borda[nova_coordenada_x][nova_coordenada_y][2] = 0

    nome_imagem = 'Borda' + str(index) + ".png"
    cv2.imwrite(nome_imagem, img_borda)   


def getColor(pixel, imagem_original, pos_x, pos_y):
    RGB = []
    #pegar a posição do pixel na imagem
    #posicao_do_pixel = posicao_pixel(imagem_original, pixel)
    pos_x = pixel[0] + 1
    pos_y = pixel[1] + 1 

    return imagem_original[pos_x,pos_y], pos_x, pos_y

def encontra_pixel(fronteira, encontrou_borda, img, pixel, col):
    x = pixel[0]
    y = pixel[1]

    #se encontrar um ponto na fronteira pegar a 
    #cor indicar que entro na imagem encontrou_borda = true            
    if boolPontoNaBorda((x,y), fronteira):
        encontrou_borda = True
        #caso ele seja a borda de saída
        if img[x, y+1] >= BRANCO:
            encontrou_borda = False
            x += 1
            y = 0
            while(boolPontoNaBorda((x,y), fronteira) == False):
                y += 1
                if(y>col):
                    return (0,0), False, encontrou_borda         
        if encontrou_borda:
            y += 1

        return (x,y), True, encontrou_borda
    
    elif encontrou_borda and boolPontoNaBorda((x,y), fronteira) == False:
        y += 1
        return (x,y), True, encontrou_borda
    
        
    return (0,0), False, encontrou_borda

def criar_imagem_unica_folha_colorida(img, imagem_original, imagem_branca, fronteira, menor_x, menor_y, maior_x, maior_y, index):
    #criar uma lista de pontos das coordenadas das cores
    print("função de criar imagem única colorida")
    encontrou_borda = False
    row, col = img.shape        
    pos_x = 0
    pos_y = 0
    esta_pintando = True
    pixel = fronteira[0]
    while(esta_pintando):
        cor_RGB, pos_x, pos_y = getColor(pixel, imagem_original, pos_x, pos_y)
        nova_coordenada_x = (int(pixel[0])-menor_x)+1
        nova_coordenada_y = (int(pixel[1])-menor_y)+1
        imagem_branca[nova_coordenada_x][nova_coordenada_y][0] = cor_RGB[0]
        imagem_branca[nova_coordenada_x][nova_coordenada_y][1] = cor_RGB[1]
        imagem_branca[nova_coordenada_x][nova_coordenada_y][2] = cor_RGB[2]
        pixel, esta_pintando, encontrou_borda = encontra_pixel(fronteira, encontrou_borda, img, pixel, col)

    nome_imagem = 'ImagemColorida' + str(index) + ".png"
    print("Salvou a imagem: ", index)
    cv2.imwrite(nome_imagem, imagem_branca)   
            


def recorta_imagem(lista_fronteiras, imagem_sem_ruido, imagem_original):
    
    print("FUNÇÃO DE RECORTAR IMAGEM")
    index = 0
    for fronteira in lista_fronteiras:
        row, col, menor_x, menor_y, maior_x, maior_y = encontra_dimensoes(fronteira)#encontar a largura e a altura 
        
        #salavando a borda
        imagem_branca = np.ones((row, col, 3)) * 255
        cv2.imwrite("Branco.png", imagem_branca)   
        
        #criar_imagem_borda(imagem_branca, fronteira, menor_x, menor_y, index)
        
        #salvando a folha
        criar_imagem_unica_folha_colorida(imagem_sem_ruido, imagem_original, imagem_branca, fronteira, menor_x, menor_y, maior_x, maior_y, index)
        index += 1 


def main():
    imagem = cv2.imread('Folhas/Teste10.png')
    #imagem = cv2.imread('teste-separar.png')
    img_sem_ruido = remove_ruidos(imagem)
    print("Bem Vindo ao Trabalho de Processamento de Imagens")
    lista_fronteiras = []
    #while(processar todas as imagens da pasta Folhas)
    lista_fronteiras = init(img_sem_ruido) #encontrar as bordas
    recorta_imagem(lista_fronteiras, img_sem_ruido, imagem) # recortar as folhas e salvar em disco (salvar a borda e a folha original)
    #analise_textura() #

    #criar_planilha() # salvar os dados 
    
    

if __name__ == "__main__":
    main()