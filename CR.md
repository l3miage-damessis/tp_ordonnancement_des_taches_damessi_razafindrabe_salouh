# Compte rendu – TP Ordonnancement de Tâches

**Membres du groupe**

- Samuel DAMESSI
- Timoty RAZAFINDRABE
- Ayman SALOUH

## Modélisation

###  Conventions de notations

| Symbole                | Description                                                           |
|------------------------|-------------|
| $\mathcal{J}$          | Ensemble des **jobs** (ou tâches), indexés par $j$                    |
| $\mathcal{M}$          | Ensemble des **machines**, indexées par $m$                           |
| $\mathcal{O}$          | Ensemble  des **opérations** indexées par $o$ |
| $\text{compat}_{j,o}$  | Ensemble des **machines compatibles** avec l’opération $o$ du job $j$ |
| $d_{j,o,m}$            | **Durée** d’exécution de l’opération $o$ du job $j$ sur la machine $m$ |
| $e_{j,o,m}$            | **Énergie** consommée pour exécuter l'operation $o$ du job $j$ sur la machine $m$ |
| $e^{\text{start}}_m$   | **Énergie** pour **allumer** la machine $m$ |
| $e^{\text{stop}}_m$    | **Énergie** pour **éteindre** la machine $m$ |
| $t^{\text{start}}_m$   | **Durée** pour **allumer** la machine $m$ |
| $t^{\text{stop}}_m$    | **Durée** pour **éteindre** la machine $m$ |
| $e^{\text{idle}}_m$    | **Énergie** par unité de temps pour une machine $m$ **inactive mais allumée** |
| $T^{\text{max}}_m$     | **Instant limite** au-delà duquel la machine $m$ **doit être arrêtée** |
| $x_{j,o,m}$            | Variable binaire : 1 si $o$ du job $j$ est affectée à $m$, 0 sinon |
| $s_{j,o}$              | Instant de **début** de l’opération $o$ du job $j$ |
| $a_m^k,\ b_m^k$        | Début et fin de la $k$-ième **plage d’activité** de la machine $m$ |
| $C_{\max}$             | **Durée totale** du planning |
| $E$                    | Consommation énergétique totale |
| $\alpha,\ \beta,\    $ | Coefficients de pondération |
| $\lambda$              | Coefficient de pénalisation pour contraintes violées |

---

### 1. Variables de décision, contraintes et objectifs

#### Variables de décision

- $x_{j,o,m} \in \{0,1\}$ : 1 si l’opération $(j,o)$ est affectée à la machine $m$, 0 sinon.
- $s_{j,o} \in \mathbb{R}^+$ : instant de début de l’opération $(j,o)$.
- $a_m^k,\ b_m^k \in \mathbb{R}^+$ : début et fin de la $k$-ième plage d’activité de la machine $m$.

## Contraintes

**1. Affectation unique**

Chaque opération doit être affectée à **exactement une machine** parmi celles compatibles avec elle.

$$
\sum_{m \in \text{compat}_{j,o}} x_{j,o,m} = 1 \quad \forall j \in \mathcal{J},\ \forall o \in \mathcal{O}_j
$$

**2. Compatibilité machine/opération**

Une opération **ne peut être affectée** qu’à une machine compatible.

$$
x_{j,o,m} = 0 \quad \text{si } m \notin \text{compat}_{j,o}
$$

**3. Précédence des opérations au sein d'une tâche**

Les opérations d’une même tâche doivent être exécutées **dans l’ordre**. Une opération ne peut commencer qu’après la fin de la précédente.

$$
s_{j,o+1} \geq s_{j,o} + \sum_{m \in \text{compat}_{j,o}} x_{j,o,m} \cdot d_{j,o,m} \quad \forall j,\ \forall o < |\mathcal{O}_j| - 1
$$

**4. Non-chevauchement sur une même machine**

Deux opérations affectées à la **même machine** ne peuvent pas être exécutées en même temps. Pour toute paire d’opérations affectées à une machine donnée, l’une doit terminer avant que l’autre ne commence.

$$
\text{Si } x_{j,o,m} = x_{j',o',m} = 1,\quad
s_{j,o} + d_{j,o,m} \leq s_{j',o'} \quad \text{ou} \quad
s_{j',o'} + d_{j',o',m} \leq s_{j,o}
$$

**5. Respect des plages actives des machines**

Une opération ne peut être exécutée que **durant une période où la machine est active** (entre l’allumage complet et l’extinction).

Pour toute opération affectée à une machine, son intervalle d’exécution `[début, fin]` doit être entièrement contenu dans une plage active de cette machine.

$$
s_{j,o} \in \bigcup_k [a_m^k + t_m^{\text{start}},\ b_m^k] \quad \text{et} \quad
s_{j,o} + d_{j,o,m} \in \bigcup_k [a_m^k + t_m^{\text{start}},\ b_m^k] \quad \text{si } x_{j,o,m} = 1
$$

**6. Limite maximale du planning machine**

Le planning d’utilisation d’une machine ne peut pas dépasser une **durée maximale autorisée** définie par l’entreprise.

Pour toute période active `k` d’une machine `m`, on impose :

$$
b_m^k \leq T_m^{\text{max}} \quad \forall m \in \mathcal{M},\ \forall k
$$



#### Objectifs

- **Minimisation de la consommation d’énergie totale** (incluant allumage, fonctionnement actif, inactivité, extinction).
- **Minimisation de la durée totale du planning**.


#### 2. Fonction objectif agrégée

Une fonction multicritère pondérée peut être proposée :

$
\min \left( \alpha \cdot E + \beta \cdot C_{\max} \right)
$


avec :
- $E$ : énergie totale consommée,
- $C_{\max}$ : durée totale du planning,
- $\alpha, \beta$ : coefficients de pondération.

---

### 3. Évaluation d’une solution

#### Solution réalisable

Une solution est **réalisable** si toutes les contraintes sont respectées.

Son évaluation repose sur :
- $E$ : somme des énergies d’allumage, de traitement, d’inactivité et d’extinction des machines utilisées,
- $C_{\max}$ : dernier instant d'activité de toutes les machines,


#### Solution non réalisable

Une solution non réalisable est évaluée à l’aide d’une fonction pénalisée :

$$
f_{\text{pénalisée}} = f + \lambda \cdot \text{Violations}
$$

où $\text{Violations}$ mesure l’ampleur des contraintes violées et $\lambda$ est un coefficient élevé.

---

### 4. Instance sans solution réalisable

#### Exemple

- 1 job $j_1$ avec 2 opérations $o_0$, $o_1$ ;
- 1 seule machine $m_1$ compatible ;
- Durées : $d_{j_1,o_0,m_1} = 60$, $d_{j_1,o_1,m_1} = 70$ ;
- Limite de disponibilité : $T^{\text{max}}_{m_1} = 100$.

#### Analyse

La somme des durées est $60 + 70 = 130$, ce qui dépasse la limite de temps autorisée.

Donc **aucune solution réalisable n’existe** dans cette instance.

## Premières heuristiques

Afin d’obtenir une solution initiale au problème d’ordonnancement, nous proposons deux heuristiques : une déterministe gloutonne et une non-déterministe. Ces heuristiques visent à générer rapidement des plannings raisonnables, qui peuvent ensuite être améliorés via des méthodes de recherche locale.

### 1. Heuristique gloutonne déterministe

#### Principe général

L’algorithme construit la solution opération par opération, en attribuant à chaque opération la machine admissible minimisant une **fonction de coût** combinant la durée d’exécution et la consommation d’énergie. Le choix est fait de manière *myope*, sans retour arrière, ce qui caractérise une approche gloutonne.

La fonction de coût utilisée est :

$Coût(o, j, m) = \alpha × e_{j,o,m} + \beta × d_{j,o,m}$
où :
- $e_{j,o,m}$ est l'énergie consommée pour exécuter l'operation $o$ du job $j$ sur la machine $m$
- $d_{j,o,m}$ est la durée d’exécution de l’opération $o$ du job $j$ sur la machine $m$
- $\alpha, \beta$ sont des coefficients positifs permettant de pondérer l’importance de la durée et de l’énergie.

#### Optimisation de la consommation passive

Lorsqu’une machine reste inactive entre deux opérations, l’algorithme évalue s’il est préférable :
- de la laisser allumée (consommation passive),
- ou de l’éteindre temporairement et de la rallumer juste à temps.

Ce choix dépend :
- du **coût énergétique d’allumage/extinction**,
- du **temps nécessaire pour rallumer** la machine,
- de la **durée d’inactivité**.

Cela permet de limiter la consommation énergétique dans les phases creuses, en intégrant une décision locale sur l’état de la machine.

#### Complexité

Soit :
- $|\mathcal{O}|$ le nombre total d'opérations
- $|\mathcal{M}|$ le nombre de machines.

Pour chaque opération, l’algorithme évalue le coût sur toutes les machines admissibles. La complexité est donc :

La complexité est donc : $O(|\mathcal{O}| × |\mathcal{M}|)$

### 2. Heuristique non-déterministe

#### Principe général

L’algorithme construit la solution opération par opération, en attribuant à chaque opération une machine admissible choisie **aléatoirement**. Aucune évaluation de coût n’est réalisée lors de cette sélection.

Le choix est uniforme parmi les machines admissibles à l’opération, ce qui permet de générer des solutions différentes à chaque exécution, sans guidage par un critère d’optimisation.

#### Optimisation de la consommation passive

Lorsqu’une machine reste inactive entre deux opérations, l’algorithme évalue s’il est préférable :
- de la laisser allumée (consommation passive),
- ou de l’éteindre temporairement et de la rallumer juste à temps.

Ce choix dépend :
- du **coût énergétique d’allumage/extinction**,
- du **temps nécessaire pour rallumer** la machine,
- de la **durée d’inactivité**.

Cela permet de limiter la consommation énergétique dans les phases creuses, en intégrant une décision locale sur l’état de la machine.


#### Complexité

Soit :
- $|\mathcal{O}|$ le nombre total d'opérations

Aucune recherche parmi les machines n’est effectuée. Chaque opération se voit attribuer une machine en temps constant (tirage aléatoire), et l’optimisation de consommation est locale.

$O(|\mathcal{O}|)$

## Recherche locale

### 1. Proposition de deux voisinages de solutions

Pour améliorer les solutions initiales obtenues par les heuristiques, nous proposons deux types de voisinages permettant d’explorer l’espace des solutions voisines.

#### Voisinage 1 : Réaffectation d’une opération

- **Principe** : On choisit une opération et on modifie la machine sur laquelle elle est exécutée, en la déplaçant vers une autre machine admissible.
- **Taille du voisinage** : Environ $|\mathcal{O}| \times (|\mathcal{M}| - 1)$, où $|\mathcal{O}|$ est le nombre total d’opérations et $|\mathcal{M}|$ le nombre de machines.
- **Complexité** : Taille polynomiale par rapport à la taille de l’instance.
- **Couverture de l’espace des solutions** : Ce voisinage permet de modifier progressivement l’affectation des opérations, mais ne suffit pas à atteindre toutes les permutations possibles, notamment les réordonnancements.

#### Voisinage 2 : Échange d’opérations entre machines

- **Principe** : On choisit deux opérations sur deux machines différentes et on échange leurs affectations (machines et éventuellement leurs positions temporelles).
- **Taille du voisinage** : Environ $O(|\mathcal{O}|^2)$ où $|\mathcal{O}|$ est le nombre total d’opérations, car on considère toutes les paires d’opérations.
- **Complexité** : Taille polynomiale.
- **Couverture de l’espace des solutions** : Ce voisinage est plus riche et permet de parcourir un plus large espace de solutions, incluant des permutations complexes, mais ne garantit pas l’accessibilité de toutes les solutions.

### 2. Implémentation des voisinages

Les deux voisinages seront implémentés dans le module `optim.neighborhoods` sous forme de générateurs de solutions voisines à partir d’une solution courante.


### 3. Implémentation des algorithmes de recherche locale

Deux algorithmes de recherche locale seront développés dans le module `optim.local_search`, utilisant la classe `NonDeterminist` pour générer la solution initiale.

- **Algorithme 1** :  
  Utilise uniquement le premier voisinage.  
  À chaque itération, explore le voisinage et accepte la **première solution améliorante** rencontrée.

- **Algorithme 2** :  
  Utilise les deux voisinages.  
  À chaque itération, explore successivement chaque voisinage et sélectionne la **meilleure solution améliorante** parmi les deux.  
  Un critère d’arrêt additionnel pourra être ajouté (par exemple nombre maximal d’itérations sans amélioration).

---

### 4. Comparaison des algorithmes
