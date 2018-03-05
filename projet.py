# coding: utf-8

from Tkinter import *
import numpy as np
from tkMessageBox import *
import copy


LONGUEUR_PLATEAU = 7
HAUTEUR_PLATEAU = 6
PUISSANCE = 4
NOMBRE_JOUEURS = 2



def signe(i):
	if i==0:
		return 0
	return i/abs(i)



#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
class Point:
	"""Attributs :
	couple int"""


	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __repr__(self):
		return "({}, {})".format(self.x, self.y)

	def equals(self, p):
		return self.x == p.x and self.y == p.y

	def distance(self, point):
		return max(abs(self.x-point.x), abs(self.y-point.y))

	def adjacents(self,point):
		"""Un point est adjacent à lui même"""
		return self.distance(point)<=1

	def coeff_dirr(self, point):
		if self.x!=point.x and self.y!=point.y and abs(self.x-point.x)!=abs(self.y-point.y) :
			print("Tentative de mauvais calcul de coefficient directeur entre {} {}".format(self, point))
		else:
			return [signe(point.x-self.x),signe(point.y-self.y)]

	def points_en_puissance(self):
		res = []
		for d in [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]]:
			p = Point(d[0]*PUISSANCE+self.x, d[1]*PUISSANCE+self.y)
			res.append(p)
		return res


def liste_points_contiens(liste, element):
	for elm in liste:
		if elm.x == element.x and elm.y == element.y :
			return True
	return False

#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
class EnsemblePoints:

	def __init__(self):
		self.elm = []

	def __getitem__(self, index):
		return self.elm[index]

	def __setitem__(self,index,val):
		self.elm[index] = val

	def __delitem__(self,index):
		self.elm.__delitem__(index)

	def append(self, elm):
		self.elm.append(elm)

	def contiens(self, elm):
		for e in self.elm:
			if e.x == elm.x and e.y == elm.y:
				return True
		return False


	def __len__(self):
		return self.elm.__len__()

	def __repr__(self):
		string = "{"
		for elm in self:
			string+="{}".format(elm)
		string+="}"
		return string

	def remove(self, point):
		for i in range(self.__len__()):
			if self.elm[i].x == point.x and self.elm[i].y == point.y :
				self.__delitem__(i)



	#	pour chaque point:
	#		pour chaque direction:
	#			compt = 0
	#			on pars du centre, on longe la direction à droite en whil
	#				si on est dans lensmble
	#					compt ++
	#				si on nest plus dans lensmble
	#					si ici vide
	#						dg += 1
	#			direction à gauche
	#				si dans ens 
	#					compt ++
	#				sinon
	#					si vide
	#						dg ++
	#					res[dg][compt] ++

	def alignes(self, plateau, joueur):
		"""En indice 1 : tab des lignes à 1 degré de liberté, 2 2 etc.. Dedans : nombre de lignes de longueur 2,3,4 etc...
		[[8,3,1],[2,1,0]]"""

		res = np.zeros((2,PUISSANCE-1))
		for point in self.elm:
			for d in [[-1,-1],[-1,0],[-1,1],[0,-1]]:
				p = Point(point.x, point.y)
				compt = 0
				dg = 0
				while plateau.contiens(p) and self.contiens(p) :
					compt+=1
					p.x -= d[0]
					p.y -= d[1]
				if plateau.contiens(p) and plateau.mat[p.x][p.y] == 0 :
					dg+=1
				p.x = point.x
				p.y = point.y
				compt-=1 #On compte 2 fois point sinon
				while plateau.contiens(p) and self.contiens(p) :
					compt+=1
					p.x += d[0]
					p.y += d[1]
				if plateau.contiens(p) and plateau.mat[p.x][p.y] == 0 :
					dg+=1
				if compt>PUISSANCE-1:
					res[0][PUISSANCE-2] += 1
				elif compt>1 and dg>0:
					res[dg-1][compt-2] += 1
		#Pour chaque ligne de n points, on la compte n fois (en chaque points), donc on divise par n
		for degre in res:
			for i in range(degre.__len__()):
				degre[i]/=(i+2)
		return res
				



#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
class Coup:
	"""Attributs :
	entier entre 0 et lenght du plateau
	joueur associé"""

	def __init__(self, x, joueur):
		self.x = x
		self.joueur = joueur

	def est_jouable(self, plateau):
		if self.x<0 or self.x>LONGUEUR_PLATEAU :
			return False
		if plateau.mat[0][self.x] != 0 :
			return False
		return True

	def __repr__(self):
		return "Coup joué en {} par {}".format(self.x, self.joueur)

	def point_resultant(self, plateau):
		if self.est_jouable(plateau) :
			j = HAUTEUR_PLATEAU-1
			while plateau.mat[j][self.x] != 0 :
				j=j-1
			return Point(j,self.x)
		else:
			#print("Le coup en {} par {} n'est pas jouable".format(self.x, self.joueur))
			return Point(-1,-1)

	def est_gagnant(self, plateau): 	
		if self.est_jouable(plateau):
			for d in [[-1,-1],[-1,0],[-1,1],[0,-1]]:
				point_res = self.point_resultant(plateau)
				p = Point((PUISSANCE)*d[0]+point_res.x, (PUISSANCE)*d[1]+point_res.y)
				compt = 0
				for i in range(PUISSANCE*2+1):
					if plateau.ens[self.joueur.numero-1].contiens(p) or point_res.equals(p):
						compt+=1
						if compt >= PUISSANCE:
							return True
					else:
						compt = 0
					p.x -= d[0]
					p.y -= d[1]
		return False





#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
class Joueur:
	"""Attributs :
	int numéro"""

	def __init__(self, numero):
		self.numero = numero

	def __repr__(self):
		return "Joueur numéro {}".format(self.numero)


def max_liste(liste, a = -10000):
	i = 0
	res = 0
	for elm in liste:
		if elm>a :
			a = elm
			res = i
		i+=1
	return res

def combinaisons_2LP():
	"""Combinaisons de lg 2 parmi range(LONGUEUR_PLATEAU)"""
	res = []
	for i in range(LONGUEUR_PLATEAU):
		for j in range(LONGUEUR_PLATEAU):
			a = [i,j]
			res.append(a)
	return res

def combinaisons_3LP():
	"""Combinaisons de lg 3 parmi range(LONGUEUR_PLATEAU)"""
	res = []
	for i in range(LONGUEUR_PLATEAU):
		for j in range(LONGUEUR_PLATEAU):
			for k in range(LONGUEUR_PLATEAU):
				a = [i,j,k]
				res.append(a)
	return res
	



#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------
class Plateau:
	"""Attributs :
	matrice de cases : 0 vide, 1 j1, 2 j2
	ensemble de pions joués pour chaque joueurs"""

	def __init__(self):
		self.mat = np.zeros((HAUTEUR_PLATEAU, LONGUEUR_PLATEAU), int)
		self.ens = []
		for i in range(NOMBRE_JOUEURS):
			self.ens.append(EnsemblePoints())

	def joue_coup(self, coup):
		plateau = copy.copy(self)
		p = coup.point_resultant(plateau)
		plateau.mat[p.x][p.y] = coup.joueur.numero
		plateau.ens[coup.joueur.numero-1].append(p)
		return plateau

	def __repr__(self):
		string = "Plateau de jeu\n"
		for i in range(HAUTEUR_PLATEAU):
			for j in range(LONGUEUR_PLATEAU):
				string+=" {}".format(self.mat[i][j])
			string+="\n"
		string+="\n"

		for i in range(NOMBRE_JOUEURS):
			string+= "Points du joueur {} {}\n".format(i+1, self.ens[i])

		return string

	def copy(self):
		p = Plateau()
		for i in range(HAUTEUR_PLATEAU):
			for j in range(LONGUEUR_PLATEAU):
				p.mat[i][j] = self.mat[i][j]

		for i in range(NOMBRE_JOUEURS):
			for elm in self.ens[i]:
				p.ens[i].append(elm)

		return p

	def contiens(self, point):
		return (point.x<HAUTEUR_PLATEAU and point.x>=0 and point.y<LONGUEUR_PLATEAU and point.y>=0)

	def poids(self, joueur, poids_victoire=1000):
		lignes_alliees = self.ens[joueur.numero-1].alignes(self, joueur.numero-1)
		lignes_enemies = self.ens[1-(joueur.numero-1)].alignes(self, 1-(joueur.numero-1))
		res = 0
		i = 0
		if lignes_alliees[0][PUISSANCE-2] != 0 or lignes_alliees[1][PUISSANCE-2] != 0 :
			return poids_victoire
		for deg in lignes_alliees :
			i+=1
			for j in range(deg.__len__()) :
				res += i*deg[j]*(j+2)*(j+2)
		i = 0

		if lignes_enemies[0][PUISSANCE-2]!=0 or lignes_enemies[1][PUISSANCE-2] != 0:
			return -poids_victoire
		for deg in lignes_enemies :
			i+=1
			for j in range(deg.__len__()) :
				res -= i*deg[j]*(j+2)*(j+2)
		return res

	def meilleur_coup_instant(self, joueur, poids_base=-10000):
		poids = poids_base
		indice = 0
		for i in range(LONGUEUR_PLATEAU):
			plateau = self.copy()
			c = Coup(i, joueur)
			if c.est_jouable(plateau):
				plateau = plateau.joue_coup(c)
				if plateau.poids(joueur) > poids :
					indice = i
					poids = plateau.poids(joueur)
		return Coup(indice,joueur)

	def meilleur_coup_deux(self, joueur, ennemi, poids_base = -10000):
		for i in range(LONGUEUR_PLATEAU):
			coup = Coup(i,joueur)
			if coup.est_gagnant(self):
				return coup
		for i in range(LONGUEUR_PLATEAU):
			coup = Coup(i,ennemi)
			if coup.est_gagnant(self):
				coup = Coup(i, joueur)
				return coup
		suite_coups_possibles = combinaisons_2LP()
		meilleur_poids = poids_base
		meilleur_coup = 0
		for elm in suite_coups_possibles:
			plateau = self.copy()
			i = 0
			poids = 0
			while i < 2:
				c = Coup(elm[i], joueur)
				plateau = plateau.joue_coup(c)
				i+=1
				c2 = plateau.meilleur_coup_instant(ennemi)
				plateau.joue_coup(c2)
			poids = plateau.poids(joueur)
			if poids>=meilleur_poids and Coup(elm[0], joueur).est_jouable(plateau):
				meilleur_coup = elm[0]
				meilleur_poids = poids

		return Coup(meilleur_coup, joueur)

"""	def meilleur_coup_trois(self, joueur, ennemi, poids_base = -10000):
		for i in range(LONGUEUR_PLATEAU):
			coup = Coup(i,joueur)
			if coup.est_gagnant(self):
				return coup
		for i in range(LONGUEUR_PLATEAU):
			coup = Coup(i,ennemi)
			if coup.est_gagnant(self):
				coup = Coup(i, joueur)
				return coup
		suite_coups_possibles = combinaisons_3LP()
		meilleur_poids = poids_base
		meilleur_coup = 0
		for elm in suite_coups_possibles:
			plateau = self.copy()
			i = 0
			poids = 0
			while i < 3:
				c = Coup(elm[i], joueur)
				plateau = plateau.joue_coup(c)
				i+=1
				c2 = plateau.meilleur_coup_instant(ennemi)
				plateau.joue_coup(c2)
			poids = plateau.poids(joueur)
			if poids>=meilleur_poids and Coup(elm[0], joueur).est_jouable(plateau):
				meilleur_coup = elm[0]
				meilleur_poids = poids

		return Coup(meilleur_coup, joueur) """


#----------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------

class Interface(Frame):
	def __init__(self, fenetre, **kwargs):
		self.plateau = Plateau()
		Frame.__init__(self, fenetre, width=0, height=0, **kwargs)
		self.pack(fill=BOTH)

		self.canvas = Canvas(fenetre,width=60*LONGUEUR_PLATEAU, height=60*HAUTEUR_PLATEAU)

		for j in xrange(LONGUEUR_PLATEAU):
			for i in xrange(HAUTEUR_PLATEAU):
				if self.plateau.mat[i][j] == 1:
					self.canvas.create_image(j*60, i*60, anchor=NW, image=pionrouge)
				elif self.plateau.mat[i][j] == 2:
					self.canvas.create_image(j*60, i*60, anchor=NW, image=pionjaune)
				else:
					self.canvas.create_image(j*60, i*60, anchor=NW, image=casevide)
		
		self.canvas.pack()

		Button(fenetre, image = toparrow, command=lambda: self.joue(0)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(1)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(2)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(3)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(4)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(5)).pack(side=LEFT)
		Button(fenetre, image = toparrow, command=lambda: self.joue(6)).pack(side=LEFT)

	def joue(self, i):
		joueur = j1
		coup = Coup(i,joueur)

		if coup.est_jouable(self.plateau):
			point = coup.point_resultant(self.plateau)
			self.canvas.create_image(point.y*60, point.x*60, anchor=NW, image=pionrouge)
			if coup.est_gagnant(self.plateau):
				showinfo("Victoire", "{} est victorieux".format(joueur))
			self.plateau = self.plateau.joue_coup(coup)

			joueur = j2
			coup = self.plateau.meilleur_coup_deux(j2, j1)
			point = coup.point_resultant(self.plateau)
			self.canvas.create_image(point.y*60, point.x*60, anchor=NW, image=pionjaune)
			if coup.est_gagnant(self.plateau):
				showinfo("Victoire", "{} est victorieux".format(joueur))
			self.plateau = self.plateau.joue_coup(coup)


		

#======================================================================================================================
#----------------------------------------------------------------------------------------------------------------------
#======================================================================================================================




j1 = Joueur(1)
j2 = Joueur(2)

fenetre = Tk()

pionrouge = PhotoImage(file="pionrouge.png")
pionjaune = PhotoImage(file="pionjaune.png")
casevide = PhotoImage(file="casevide.png")
toparrow = PhotoImage(file="toparrow.png")




interface = Interface(fenetre)
interface.mainloop()

"""
p = Plateau()
print(p)

contuinuer = 1
while contuinuer:
	inp = input("Jouer un coup\n")
	a = int(inp)
	c = Coup(a,j1)
	if c.est_gagnant(p):
		contuinuer = 0
	p = p.joue_coup(c)

	print(p.ens[0].alignes(p, j1))


	c = p.meilleur_coup_deux(j2,j1)
	if c.est_gagnant(p):
		contuinuer = 0
	p = p.joue_coup(c)
	print(p.ens[0].alignes(p, j2))

	print(p)

"""