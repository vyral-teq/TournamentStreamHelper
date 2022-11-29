import requests
import os
import traceback
import re
import json
from ..Helpers.TSHDictHelper import deep_get
from ..TSHGameAssetManager import TSHGameAssetManager
from ..TSHPlayerDB import TSHPlayerDB
from .TournamentDataProvider import TournamentDataProvider
from PyQt5.QtCore import *
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from ..Workers import Worker

def CHALLONGE_BRACKET_TYPE(bracketType: str):
    mapping = {
        "DoubleEliminationBracketPlotter": "DOUBLE_ELIMINATION"
    }
    if bracketType in mapping:
        return mapping[bracketType]
    else:
        return bracketType

class ChallongeDataProvider(TournamentDataProvider):

    def __init__(self, url, threadpool, parent) -> None:
        super().__init__(url, threadpool, parent)
        self.name = "Challonge"

    def GetTournamentData(self, progress_callback=None):
        finalData = {}

        try:
            slug = re.findall(r"challonge\.com\/.*\/([^/]+)", self.url)
            if len(slug) > 0:
                slug = slug[0]

                data = requests.get(
                    f"https://challonge.com/en/search/tournaments.json?filters%5B&page=1&per=1&q={slug}",
                    headers={
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                        "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                        "Accept-Encoding": "gzip, deflate, br"
                    }
                )

                data = json.loads(data.text)

                collection = deep_get(data, "collection", [{}])[0]

                videogame = collection.get("filter", {}).get("id", None)
                if videogame:
                    TSHGameAssetManager.instance.SetGameFromChallongeId(
                        videogame)
                    self.videogame = videogame

                finalData["tournamentName"] = deep_get(collection, "name")

                details = collection.get("details", [])
                participantsElement = next(
                    (d for d in details if d.get("icon") == "fa fa-users"), None)
                if participantsElement:
                    participants = int(
                        participantsElement.get("text").split(" ")[0])
                    finalData["numEntrants"] = participants
                # finalData["address"] = deep_get(
                #     data, "data.event.tournament.venueAddress", "")
        except:
            traceback.print_exc()

        return finalData

    def GetMatch(self, setId, progress_callback):
        finalData = {}

        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )
            data = json.loads(data.text)

            all_matches = self.GetAllMatchesFromData(data)

            match = next((m for m in all_matches if str(
                m.get("id")) == str(setId)), None)

            if match:
                finalData = self.ParseMatchData(match)
        except:
            traceback.print_exc()

        print(finalData)

        return finalData

    def GetMatches(self, getFinished=False, progress_callback=None):
        final_data = []

        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )

            data = json.loads(data.text)

            all_matches = self.GetAllMatchesFromData(data)

            states = ["open", "pending"]

            if getFinished:
                states.append("complete")

            all_matches = [
                match for match in all_matches if match.get("state") in states and match.get("player1") and match.get("player2")]

            for match in all_matches:
                final_data.append(self.ParseMatchData(match))

            final_data.reverse()
        except Exception as e:
            traceback.print_exc()

        return final_data
    
    def GetTournamentPhases(self, progress_callback=None):
        phases = []

        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )
            print(data.text)
            data = json.loads(data.text)

            if len(deep_get(data, "groups", [])) > 0:
                phaseObj = {
                    "id": "group_stage",
                    "name": "Group Stage",
                    "groups": []
                }
                for g, group in enumerate(deep_get(data, "groups", [])):
                    phaseObj["groups"].append({
                        "id": g,
                        "name": group.get('name'),
                        "bracketType": CHALLONGE_BRACKET_TYPE(group.get("requested_plotter"))
                    })
                phases.append(phaseObj)
            
            phases.append({
                "id": "final_stage",
                "name": "Final Stage",
                "groups": [{
                        "id": "final_stage",
                        "name": "Bracket",
                        "bracketType": CHALLONGE_BRACKET_TYPE(data.get("requested_plotter"))
                    }
                ]
            })
        except:
            traceback.print_exc()

        return phases

    def GetTournamentPhaseGroup(self, id, progress_callback=None):
        finalData = {}
        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )
            print(data.text)
            data = json.loads(data.text)

            if id == "final_stage":
                pass
            else:
                deep_get(data, "groups", [])[int(id)]

            entrants = self.GetAllEntrantsFromData(data)
            entrants.sort(key=lambda e: e.get("seed"))

            finalData["entrants"] = entrants

            all_matches = self.GetAllMatchesFromData(data)

            parsed_matches = []

            for match in all_matches:
                parsed_matches.append(self.ParseMatchData(match))

            parsed_matches.sort(key=lambda match: abs(int(match.get("round"))), reverse=True)

            rounds = {}

            for match in parsed_matches:
                roundNum = match.get("round")

                score = [match.get("team1score", -1), match.get("team2score", -1)]

                if int(roundNum) == -2:
                    score.reverse()
                
                if roundNum < 0:
                    roundNum -= 3

                # For first round, we work around the incomplete data Challonge gives us
                if roundNum == 1:
                    nextRoundMatches = [s for s in parsed_matches if s.get("round") == roundNum+1]
                    
                    # Initially, fill in the round with -1 scores
                    if not str(roundNum) in rounds:
                        rounds[str(roundNum)] = []

                        # Round 1 has 2x the number of sets that Round 2 has
                        for i in range(len(nextRoundMatches) * 2):
                            rounds[str(roundNum)].append({
                                "score": [-1, -1]
                            })
                    
                    roundY = 0

                    for m, roundMatch in enumerate(nextRoundMatches):
                        if roundMatch.get("player1_prereq_identifier") == match.get("identifier"):
                            roundY = 2*m
                            break
                        if roundMatch.get("player2_prereq_identifier") == match.get("identifier"):
                            roundY = 2*m+1
                            break

                    rounds[str(roundNum)][roundY]["score"] = score
                # For first *losers* round, we work around the incomplete data Challonge gives us
                # (-1) - 3 = -4
                if roundNum == -4:
                    nextRoundMatches = [s for s in parsed_matches if s.get("round") == roundNum+3-1]
                    
                    # Initially, fill in the round with -1 scores
                    if not str(roundNum) in rounds:
                        rounds[str(roundNum)] = []

                        # Round -1 has 2x the number of sets that Round -2 has
                        for i in range(len(nextRoundMatches) * 2):
                            rounds[str(roundNum)].append({
                                "score": [-1, -1]
                            })
                    
                    roundY = 0

                    for m, roundMatch in enumerate(nextRoundMatches):
                        if roundMatch.get("player1_prereq_identifier") == match.get("identifier"):
                            roundY = 2*m-1
                            break
                        if roundMatch.get("player2_prereq_identifier") == match.get("identifier"):
                            roundY = 2*m
                            break

                    rounds[str(roundNum)][roundY]["score"] = score
                else:
                    if not str(roundNum) in rounds:
                        rounds[str(roundNum)] = []
                    
                    rounds[str(roundNum)].append({
                        "score": score
                    })
            
            print("finalRounds")
            print(rounds)

            finalData["sets"] = rounds
        except:
            traceback.print_exc()

        return finalData

    def GetAllMatchesFromData(self, data):
        rounds = deep_get(data, "rounds", {})
        matches = deep_get(data, "matches_by_round", {})

        all_matches = []

        for r, round in enumerate(matches.values()):
            for m, match in enumerate(round):
                match["round_name"] = next(
                    r["title"] for r in rounds if r["number"] == match.get("round"))
                match["round"] = match.get("round")
                if data.get("tournament", {}).get("tournament_type") == "round robin":
                    match["phase"] = "Round Robin"
                else:
                    match["phase"] = "Bracket"
                if r == len(matches.values()) - 1:
                    if m == 0:
                        match["isGF"] = True
                    elif m == 1:
                        match["isGFR"] = True
                all_matches.append(match)

        for group in deep_get(data, "groups", []):
            rounds = deep_get(group, "rounds", {})
            matches = deep_get(group, "matches_by_round", {})

            for round in matches.values():
                for match in round:
                    match["round_name"] = next(
                        r["title"] for r in rounds if r["number"] == match.get("round"))
                    match["phase"] = group.get("name")
                    all_matches.append(match)

        return all_matches

    def GetStreamMatchId(self, streamName):
        sets = self.GetMatches()

        streamSet = next(
            (s for s in sets if s.get("stream", None) ==
             streamName and s.get("is_current_stream_game")),
            None
        )

        return streamSet

    def GetUserMatchId(self, user):
        sets = self.GetMatches()

        userSet = next(
            (s for s in sets if s.get("p1_name")
             == user or s.get("p2_name") == user),
            None
        )

        if userSet and user == userSet.get("p2_name"):
            userSet["reverse"] = True

        return userSet

    def ParseMatchData(self, match):
        p1_split = deep_get(
            match, "player1.display_name").rsplit("|", 1)

        p1_gamerTag = p1_split[-1].strip()
        p1_prefix = p1_split[0].strip() if len(p1_split) > 1 else None
        p1_avatar = deep_get(match, "player1.portrait_url")
        p1_id = deep_get(match, "player1.id")

        p2_split = deep_get(
            match, "player2.display_name").rsplit("|", 1)

        p2_gamerTag = p2_split[-1].strip()
        p2_prefix = p2_split[0].strip() if len(p2_split) > 1 else None
        p2_avatar = deep_get(match, "player2.portrait_url")
        p2_id = deep_get(match, "player2.id")

        stream = deep_get(match, "station.stream_url", None)

        if not stream:
            stream = deep_get(
                match, "queued_for_station.stream_url", None)

        if stream:
            stream = stream.split("twitch.tv/")[1].replace("/", "")

        team1losers = False
        team2losers = False

        if match.get("isGF"):
            team1losers = False
            team2losers = True
        elif match.get("isGFR"):
            team1losers = True
            team2losers = True

        scores = match.get("scores")
        if len(match.get("scores")) < 2:
            scores = [None, None]

        return({
            "id": deep_get(match, "id"),
            "round_name": deep_get(match, "round_name"),
            "round": deep_get(match, "round"),
            "tournament_phase": match.get("phase"),
            "p1_name": deep_get(match, "player1.display_name"),
            "p2_name": deep_get(match, "player2.display_name"),
            "p1_seed": deep_get(match, "player1.seed"),
            "p2_seed": deep_get(match, "player2.seed"),
            "entrants": [
                [{
                    "id": [p1_id],
                    "gamerTag": p1_gamerTag,
                    "prefix": p1_prefix,
                    "avatar": p1_avatar,
                    "seed": deep_get(match, "player1.seed")
                }],
                [{
                    "id": [p2_id],
                    "gamerTag": p2_gamerTag,
                    "prefix": p2_prefix,
                    "avatar": p2_avatar,
                    "seed": deep_get(match, "player2.seed")
                }],
            ],
            "stream": stream,
            "is_current_stream_game": True if deep_get(match, "station.stream_url", None) else False,
            "team1score": scores[0],
            "team2score": scores[1],
            "team1losers": team1losers,
            "team2losers": team2losers,
            "identifier": match.get("identifier"),
            "player1_prereq_identifier": match.get("player1_prereq_identifier"),
            "player2_prereq_identifier": match.get("player2_prereq_identifier")
        })

    def GetEntrants(self):
        worker = Worker(self.GetEntrantsWorker)
        self.threadpool.start(worker)

    def GetEntrantsWorker(self, progress_callback):
        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )
            print(data)

            data = json.loads(data.text)
            TSHPlayerDB.AddPlayers(self.GetAllEntrantsFromData(data))
        except Exception as e:
            traceback.print_exc()
    
    def GetAllEntrantsFromData(self, data):
        final_data = []

        all_matches = self.GetAllMatchesFromData(data)
        all_matches.sort(key=lambda m: abs(m.get("identifier")), reverse=True)

        # do not add duplicates
        added_list = []

        for m in all_matches:
            for p in ["player1", "player2"]:
                player = m.get(p)

                if player.get("id", None) != None and not player.get("id") in added_list:
                    playerData = {}

                    split = player.get("display_name").rsplit("|", 1)

                    gamerTag = split[-1].strip()
                    prefix = split[0].strip() if len(
                        split) > 1 else None

                    playerData["gamerTag"] = gamerTag
                    playerData["prefix"] = prefix

                    playerData["avatar"] = player.get("portrait_url")

                    playerData["seed"] = player.get("seed")

                    final_data.append({
                        "players": [playerData],
                        "seed": player.get("seed")
                    })
                    added_list.append(player.get("id"))
        
        return(final_data)

    def GetStandings(self, playerNumber, progress_callback):
        final_data = []

        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )

            data = json.loads(data.text)

            all_matches = self.GetAllMatchesFromData(data)

            all_matches.sort(key=lambda m: abs(m.get("identifier")), reverse=True)

            # do not add duplicates
            added_list = []

            for m in all_matches:
                winner = m.get("player1")

                if m.get("winner_id") == m.get("player2").get("id"):
                    winner = m.get("player2")
                
                if not winner.get("id") in added_list:
                    playerData = {}

                    split = winner.get("display_name").rsplit("|", 1)

                    gamerTag = split[-1].strip()
                    prefix = split[0].strip() if len(
                        split) > 1 else None

                    playerData["gamerTag"] = gamerTag
                    playerData["prefix"] = prefix

                    playerData["avatar"] = winner.get("portrait_url")

                    final_data.append({
                        "players": [playerData]
                    })
                    added_list.append(winner.get("id"))

            return final_data
        except Exception as e:
            traceback.print_exc()
    
    def GetLastSets(self, playerID, playerNumber, callback, progress_callback):
        try:
            data = requests.get(
                self.url+".json",
                headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
                    "sec-ch-ua": 'Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
                    "Accept-Encoding": "gzip, deflate, br"
                }
            )

            data = json.loads(data.text)

            set_data = []

            all_matches = self.GetAllMatchesFromData(data)

            all_matches = [
                match for match in all_matches if match.get("state") in ["complete"] and match.get("player1") and match.get("player2")]
            
            all_matches.sort(key=lambda m: abs(m.get("identifier")), reverse=True)

            for _set in all_matches:
                _set = self.ParseMatchData(_set)

                if not _set:
                    continue
                if not _set.get("team1score") and not _set.get("team2score"):
                    continue

                if _set.get("entrants")[0][0].get("id")[0] != playerID and _set.get("entrants")[1][0].get("id")[0] != playerID:
                    continue
            
                players = ["1", "2"]
                
                if _set.get("entrants")[0][0].get("id")[0] != playerID:
                    players.reverse()
                
                player_set = {
                    "phase_id": "",
                    "phase_name": _set.get("tournament_phase"),
                    "round_name": _set.get("round_name"),
                    f"player{players[0]}_score": _set.get("team1score"),
                    f"player{players[0]}_team": _set.get("entrants")[0][0].get("prefix"),
                    f"player{players[0]}_name": _set.get("entrants")[0][0].get("gamerTag"),
                    f"player{players[1]}_score": _set.get("team2score"),
                    f"player{players[1]}_team": _set.get("entrants")[1][0].get("prefix"),
                    f"player{players[1]}_name": _set.get("entrants")[1][0].get("gamerTag"),
                }

                set_data.append(player_set)

            callback.emit({"playerNumber": playerNumber, "last_sets": set_data})
        except Exception as e:
            traceback.print_exc()
            callback.emit({"playerNumber": playerNumber,"last_sets": []})