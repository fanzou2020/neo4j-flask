## Queries
* Create query of friend recommendation
```
MATCH (f:User) -[:FRIEND*2]- (u:User{user_id:'FOBRPlBHa3WPHFB5qYDlVg'}) 
RETURN f, COUNT(*) AS occ ORDER BY occ DESC`
```

* add review count property to Business node
```
MATCH (b:Business) 
	CALL {
		WITH b MATCH (b) <-[r:REVIEW]- (:User) RETURN COUNT(r) as review_count
	}
SET b.review_count = review_count
```

* Create index for Category
```
CREATE INDEX FOR (c:Category) ON (c.category_name)
```


* Query Business by category and city, return business nodes sorted by their review_count
```
MATCH (b:Business {city:'Glendale'}) -[:HAS_CATEGORY]-> (:Category{category_name:'Pets'}) 
RETURN b ORDER BY b.review_count DESC
```

