from neo4j import GraphDatabase


class Neo4jDriver:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # def execute_query(self, query, data):
    #     with self.driver.session() as session:
    #         session.write_transaction(self._execute_query, query, data)
    #
    # @staticmethod
    # def _execute_query(tx, query, data):
    #     tx.run(query, data)

    # find user node by user_id
    def find_user(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_user, user_id)
        if len(result) != 0:
            return result[0]
        else:
            return None

    @staticmethod
    def _find_user(tx, user_id):
        result = tx.run("MATCH (u:User) WHERE u.user_id = $user_id RETURN u", user_id=user_id)
        return [record["u"] for record in result]

    # find 25 users, return list of user node
    def find_users(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_users)
        return result

    @staticmethod
    def _find_users(tx):
        result = tx.run("MATCH (n:User) RETURN n LIMIT 25")
        return [record["n"] for record in result]

    # given a user_id, find his or her friends, return the name of friends as a list
    def get_friends(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_friends, user_id)
        return result

    @staticmethod
    def _get_friends(tx, user_id):
        result = tx.run("MATCH (f:User) -[:FRIEND]- (u:User{ user_id: $user_id }) "
                        "RETURN f.name AS name", user_id=user_id)
        return [record["name"] for record in result]

    # given a user_id, find friends recommendations, return list of dic with key "user_node" and "occ".
    def friend_recommendation(self, user_id):
        with self.driver.session() as session:
            result = session.read_transaction(self._friend_recommendation, user_id)
        return result

    @staticmethod
    def _friend_recommendation(tx, user_id):
        result = tx.run("MATCH (f:User) -[:FRIEND*2]- (u:User{ user_id: $user_id }) "
                        "WHERE NOT (u) -[:FRIEND]- (f) "
                        "RETURN f, COUNT(*) AS occ ORDER BY occ DESC LIMIT 30", user_id=user_id)
        return [{"user_node": record["f"], "occ": record["occ"]} for record in result]

    # given 2 user_id, add friend relationship
    def add_friend(self, user_id, friend_id):
        with self.driver.session() as session:
            result = session.write_transaction(self._add_friend, user_id, friend_id)
        return result

    @staticmethod
    def _add_friend(tx, user_id, friend_id):
        result = tx.run("MATCH (u:User { user_id: $user_id}) \n"
                        "MATCH (f:User { user_id: $friend_id })  \n"
                        "MERGE (u) -[:FRIEND]- (f) \n"
                        "RETURN u, f",
                        user_id=user_id,
                        friend_id=friend_id)
        return [(record["u"], record["f"]) for record in result]

    # find all states, return a list of states
    def get_states(self):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_states)
        return result

    @staticmethod
    def _get_states(tx):
        result = tx.run("MATCH (b:Business) RETURN DISTINCT(b.state) AS state")
        return [record["state"] for record in result]

    # find cities by state, return a list of cities
    def get_cities_by_state(self, state):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_cities_by_state, state)
        return result

    @staticmethod
    def _get_cities_by_state(tx, state):
        result = tx.run("MATCH (b:Business{state:$state}) RETURN DISTINCT (b.city) as city", state=state)
        return [record["city"] for record in result]

    # find categories by city, return a list of categories
    def get_categories_by_city(self, city):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_categories_by_city, city)
        return result

    @staticmethod
    def _get_categories_by_city(tx, city):
        result = tx.run("MATCH (:Business{city:$city}) -[:HAS_CATEGORY]-> (c:Category) "
                        "RETURN DISTINCT (c.category_name) as category", city=city)
        return [record["category"] for record in result]

    # find business data, given state, city and category
    def get_business(self, state, city, category):
        with self.driver.session() as session:
            result = session.read_transaction(self._get_business, state, city, category)
        return result

    @staticmethod
    def _get_business(tx, state, city, category):
        result = tx.run("MATCH (b:Business{state:$state, city:$city}) -[:HAS_CATEGORY]-> "
                        "(:Category{category_name:$category}) RETURN b ORDER BY b.review_count DESC",
                        state=state,
                        city=city,
                        category=category)
        return [record["b"] for record in result]
