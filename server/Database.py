from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

class Database:
    def __init__(self, mongo_client: AsyncIOMotorClient, dev: bool):
        # Initialize the class with a MongoClient object 
        self.client = mongo_client
        # Set the database to the dev database if dev is True, otherwise set it to the prod database (in order to avoid overwriting the prod database because I'm a dumbass)
        if dev:
            self.db = self.client["dev"]
        else:
            self.db = self.client["prod"]

        self.collection = self.db["matchup-statistics"]
    
    def __normalize_team_names(self, teams: tuple[str, str]) -> str:
        string = teams[0].lower().replace(" ", "") + teams[1].lower().replace(" ", "")
        return "".join(sorted(string))
    
    def __normalize_player_name(self, player: str, id: str) -> str:
        return player.lower().replace(" ", "") + id
    
    def __matchup(self, teams: tuple[str, str], player: str) -> str:
        template = {
            "team_combination": self.__normalize_team_names(teams),
            "total_picks": 1,
            "players": {
                player: {
                    "pick_frequency": 1
                }
            }
        }
        return template
    
    # Query the MongoDB database to find the player if they exist in the team combination
    async def __find_player(self, teams: tuple[str, str], player: str):
        matchup = self.__normalize_team_names(teams)
        return await self.collection.find_one({"team_combination": matchup, f"players.{player}": {"$exists": True}})

    async def __add_matchup(self, team1: str, team2: str, player: str):
        await self.collection.insert_one(self.__matchup((team1, team2), player))

    async def update_matchup(self, teams: tuple[str, str], player: str, id: str):
        original_player_name = player  # Preserve original player name
        player = self.__normalize_player_name(player, id)
        matchup = self.__normalize_team_names(teams)
        if await self.collection.find_one({"team_combination": matchup}):
            if await self.__find_player(teams, player):
                return await self.collection.update_one(
                    {"team_combination": matchup}, 
                    {
                        "$inc": {"total_picks": 1, f"players.{player}.pick_frequency": 1}, 
                        "$set": {f"players.{player}.un_normalized_name": original_player_name}
                    }
                )
            return await self.collection.update_one(
                {"team_combination": matchup}, 
                {
                    "$inc": {"total_picks": 1}, 
                    "$set": {f"players.{player}": {"pick_frequency": 1, "un_normalized_name": original_player_name}}
                }
            )
        return await self.__add_matchup(teams[0], teams[1], player)
    
    async def calculate_rarity_score(self, teams: tuple[str, str], player: str, id: str):
        matchup = self.__normalize_team_names(teams)
        player = self.__normalize_player_name(player, id)
        data = await self.collection.find_one({"team_combination": matchup})
        if data:
            if await self.collection.find_one({"team_combination": matchup, f"players.{player}": {"$exists": True}}):
                total_picks = data["total_picks"]
                pick_frequency = data["players"][player]["pick_frequency"]
                score: float = round((pick_frequency / total_picks) * 100, 2)
                if score > 1:
                    return int(score)
                return score
        return 100
    
    async def get_top_player(self, teams: tuple[str, str]):
        matchup = self.__normalize_team_names(teams)
        data = await self.collection.find_one({"team_combination": matchup})
        if data:
            top_player = max(data["players"], key=lambda x: data["players"][x]["pick_frequency"])
            top_player = data["players"][top_player]["un_normalized_name"]
            return top_player
        return None
