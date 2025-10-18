
# IPL Auction System

**Database Management Project**  

![MySQL](https://img.shields.io/badge/Database-MySQL-blue)
![Python](https://img.shields.io/badge/Backend-Python-green)
![Flask](https://img.shields.io/badge/Framework-Flask-orange)
![HTML/CSS](https://img.shields.io/badge/Frontend-HTML%2FCSS-red)

**Technologies/Tools Used:** MySQL 8.0, Python (Flask-SQLAlchemy), HTML, CSS (Bootstrap)

## Problem Statement
The Indian Premier League (IPL) is one of the most popular cricket leagues in the world, featuring some of the best cricket players globally. The IPL auction is an integral part of the league where franchises bid for players to form their teams.

This project involves designing and developing a database for an IPL auction system using all the basic RDBMS concepts and executing all CRUD operations. The database stores and retrieves data related to the IPL auction process, including player information, franchise information, and auction results.


## Key Features
- **Team Creation:** Users can create cricket teams by entering team name, owner name, and owner email address.  
- **Player Management:** Add, remove, and edit player details, such as name, age, playing position, and statistics.  
- **Auction Management:** Conduct player auctions, allowing teams to buy players.  
- **Player Statistics:** Comprehensive statistics for each player, including performance history, average runs, and wickets.  
- **User-Friendly Interface:** Intuitive and easy-to-navigate interface for managing teams.


## Entity-Relationship Diagram
*(Include your ER diagram image here if available)*


## Database Requirements
- **Player Table:** Stores information about all players up for auction, including name, playing position, base price, nationality, and performance details.  
- **Franchise Table:** Stores information about franchises, including name, owner, budget, and other relevant details.  
- **Auction Result Table:** Stores auction results, including players sold, final bid amounts, and the franchises that bought them.


## Normalization
- **First Normal Form (1NF):** Each table cell contains a single, indivisible value. Each column has a unique name. Tables are in 1NF.  
- **Second Normal Form (2NF):** Already in 1NF. All non-key columns depend on the entire primary key. Tables are in 2NF.  
- **Third Normal Form (3NF):** Already in 2NF. All non-key columns depend only on the primary key. Tables are in 3NF.


## Normalized Tables
**OWNER**  
- ownerID, ownerName, ownerEmail, ownerPass  

**TEAMS**  
- teamID, teamName, ownerID, totBudget  

**OWNERSHIP**  
- ownerID, teamID  

**PLAYERS**  
- playerID, playerName, playerType, playerNation, playerImage, basePrice  

**SKILLS**  
- playerID, avgRuns, avgWickets, matches  

**SOLD_PLAYERS**  
- playerID, teamID, sellingP  



## Database Table Creation Queries
1. **OWNER Table**

CREATE TABLE owner (
    ownerID INT PRIMARY KEY AUTO_INCREMENT,
    ownerName VARCHAR(100) NOT NULL,
    ownerEmail VARCHAR(100) NOT NULL UNIQUE,
    ownerPass VARCHAR(10) NOT NULL
);

2. **TEAMS Table**

CREATE TABLE teams (
    teamID INT PRIMARY KEY AUTO_INCREMENT,
    teamName VARCHAR(100) NOT NULL UNIQUE,
    ownerID INT NOT NULL UNIQUE,
    totBudget INT NOT NULL DEFAULT 40,
    FOREIGN KEY (ownerID) REFERENCES owner(ownerID)
);

3. **PLAYERS Table**

CREATE TABLE players (
    playerID INT PRIMARY KEY AUTO_INCREMENT,
    playerName VARCHAR(100) NOT NULL,
    playerType VARCHAR(50) NOT NULL,
    playerNation VARCHAR(20) NOT NULL,
    basePrice INT NOT NULL,
    playerAvail VARCHAR(3) NOT NULL DEFAULT "YES",
    playerImage LONGBLOB NOT NULL
);

4. **OWNERSHIP Table**

CREATE TABLE ownership (
    teamID INT,
    ownerID INT,
    PRIMARY KEY (ownerID, teamID),
    FOREIGN KEY (teamID) REFERENCES teams(teamID)
);

5. **SKILLS Table**

CREATE TABLE skills (
    playerID INT PRIMARY KEY AUTO_INCREMENT,
    avgRuns INT NOT NULL,
    avgWickets INT NOT NULL,
    matches INT NOT NULL,
    FOREIGN KEY(playerID) REFERENCES players(playerID)
);

6. **SOLD_PLAYERS Table**

CREATE TABLE sold_players (
    playerID INT NOT NULL,
    teamID INT NOT NULL,
    sellingP INT NOT NULL,
    PRIMARY KEY(playerID, teamID)
);


## Stored Procedures

* **makeBid:** Assigns a player to the team that wins the bid.
* **releasePlayer:** Releases a player from a team and updates the budget.

## Sample Queries

* Get all players, sold players, unsold players, players’ stats, players by team, Indian/foreign players, teams, budgets, and more.
* Update base price or player statistics.
* Remove players from the database or from a team.

## Tools Used

* **Database:** MySQL 8.0
* **Backend:** Python (Flask-SQLAlchemy)
* **Frontend:** HTML, CSS (Bootstrap template)

```


```
