CREATE TABLE IF NOT EXISTS spr_user_states
(
	id serial primary key, -- record id
	user_state_id	integer, --user state id
	user_state_nm	varchar(100), -- user state's describe
		CONSTRAINT UQ_ID_USR_ST unique (user_state_id) --only one iser_state_id
);	
CREATE TABLE IF NOT EXISTS spr_relations
(
	id serial primary key, -- record id
	relation_id	integer, --relation id
	relation_nm	varchar(100), -- relation's describe
		CONSTRAINT UQ_ID_REL unique (relation_id) --only one relation_id
);
CREATE TABLE IF NOT EXISTS spr_sexes
(
	id serial primary key, -- record id
	sex_id integer, --sex id
	sex_nm varchar(100), --sex description
		CONSTRAINT SEX_ID_UNQ unique (sex_id) -- only one sex_id
);
--the user from whom the search will be conducted 
CREATE TABLE IF NOT EXISTS vkinder_search_user
(
	id serial primary key, -- record id
	vk_id integer, --id VKontakte
	first_name varchar(100), --Family name
	second_name varchar(100), --name
	city varchar(100), --city
	age integer, --age of user
	sex integer REFERENCES spr_sexes(sex_id), --sex id of user 
	relation integer REFERENCES spr_relations(relation_id), -- relation
	user_state integer REFERENCES spr_user_states(user_state_id), -- user's state
		CONSTRAINT VK_ID_UNQ unique (vk_id)
);
--search conditions of vkinder_search_user
CREATE TABLE IF NOT EXISTS vkinder_search_conditions
(
	id serial primary key, --record id
	id_search_user integer REFERENCES vkinder_search_user(vk_id), --the user from whom the search will be conducted 
	city varchar(100), --city
	age_range int4range,  --age range
	sex integer REFERENCES spr_sexes(sex_id), --sex id of user 
	relation integer REFERENCES spr_relations(relation_id), --relation
	is_open boolean default True -- condition now in use
);
--pairs were founded, but search_user didn't choice them 
CREATE TABLE IF NOT EXISTS vkinder_searched_pairs
(
	id serial primary key, -- record id
	is_offered boolean default False, --is that pair was offered to user?
	id_search_condition integer REFERENCES vkinder_search_conditions(id), --the user from whom the search will be conducted 
	id_pair integer, --id VKontakte (pair)
	first_name varchar(100), --pair's Family name
	second_name varchar(100), --pair's name
	age integer, --age of pair
	sex integer REFERENCES spr_sexes(sex_id), --sex id of pair 
	city varchar(100), --pair's city
	relation integer REFERENCES spr_relations(relation_id), --pair's relation
	photo1 varchar(500), --link to the photo1,
	likes1 integer, --amount of likes of photo1,
	photo2 varchar(500), --link to the photo2,
	likes2 integer, --amount of likes of photo2,
	photo3 varchar(500), --link to the photo3,
	likes3 integer, --amount of likes of photo3
		CONSTRAINT UQ_COND_ID_USR unique (id_search_condition, id_pair) --the same pair can be only once in each search condition
);
--the list of black pairs
CREATE TABLE IF NOT EXISTS vkinder_blacklist_pair
(
	id serial primary key, -- record id
	id_search_user integer REFERENCES vkinder_search_user(vk_id), --the user from whom the search will be conducted 
	id_pair integer, --id VKontakte (pair)
	first_name varchar(100), --pair's Family name
	second_name varchar(100), --pair's name
	age integer, --age of pair
	sex integer REFERENCES spr_sexes(sex_id), --sex id of pair 
	city varchar(100), --pair's city
	relation integer REFERENCES spr_relations(relation_id), --pair's relation 
		CONSTRAINT UQ_BLACK_ID_USR unique (id_search_user, id_pair) --the same pair can be only once
);
--the user was founded 
CREATE TABLE IF NOT EXISTS vkinder_pair
(
	id serial primary key, -- record id
	id_search_user integer REFERENCES vkinder_search_user(vk_id), --the user from whom the search will be conducted 
	id_pair integer, --id VKontakte (pair)
	first_name varchar(100), --pair's Family name
	second_name varchar(100), --pair's name
	age integer, --age of pair
	sex integer REFERENCES spr_sexes(sex_id), --sex id of pair 
	city varchar(100), --pair's city
	relation integer REFERENCES spr_relations(relation_id), --pair's relation 
		CONSTRAINT UQ_ID_USR unique (id_search_user, id_pair) --the same pair can be only once
);
--photos from pair's user
CREATE TABLE IF NOT EXISTS vkinder_photos
(
	id serial primary key, -- record id
	id_pair integer, --id pair
	photo_link varchar(1000), -- URI of the photo
	photo_likes integer -- count of likes fot that pphoto
);