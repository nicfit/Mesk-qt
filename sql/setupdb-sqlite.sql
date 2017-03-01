
CREATE TABLE artists (
   id         INTEGER PRIMARY KEY,
   name       VARCHAR(128) NOT NULL UNIQUE,
   date_added TIMESTAMP,
   sync       BOOLEAN,
   fuzzy_name VARCHAR(128) NOT NULL,
   sort_name  VARCHAR(128) NOT NULL
);

CREATE TABLE albums (
   id         INTEGER PRIMARY KEY,
   name       VARCHAR(128) NOT NULL,
   artist_id  INTEGER UNSIGNED NOT NULL REFERENCES artists(id),
   year       YEAR(4),
   date_added TIMESTAMP,
   sync       BOOLEAN,
   fuzzy_name VARCHAR(128) NOT NULL,
   small_cover VARCHAR(255) UNIQUE,
   medium_cover VARCHAR(255) UNIQUE,
   large_cover VARCHAR(255) UNIQUE,
   compilation BOOLEAN NOT NULL
);

CREATE TABLE tracks (
   id           INTEGER PRIMARY KEY,
   name         VARCHAR(128) NOT NULL,
   path         VARCHAR(255) NOT NULL UNIQUE,
   artist_id    INTEGER UNSIGNED NOT NULL REFERENCES artists(id),
   album_id     INTEGER UNSIGNED NOT NULL REFERENCES albums(id),
   track_num    SMALLINT UNSIGNED,
   track_total  SMALLINT UNSIGNED,
   time         INTEGER NOT NULL,
   date_added   DATE NOT NULL,
   sync         BOOLEAN,
   bitrate      SMALLINT UNSIGNED NOT NULL,
   vbr          BOOLEAN,
   sample_freq  MEDIUMINT UNSIGNED NOT NULL,
   mode         VARCHAR(30),
   audio_type   VARCHAR(3),
   tag_version  VARCHAR(15),
   play_count   INT UNSIGNED NOT NULL,
   play_date    TIMESTAMP,
   genre_id     TINYINT UNSIGNED REFERENCES genres(id),
   file_size    INTEGER UNSIGNED NOT NULL,
   year         YEAR(4),
   fuzzy_name   VARCHAR(128) NOT NULL,
   mod_time     INTEGER UNSIGNED NOT NULL
);

CREATE TABLE playlists (
   id INTEGER PRIMARY KEY,
   name VARCHAR(64) NOT NULL UNIQUE,
   current_track INTEGER UNSIGNED NOT NULL
);
INSERT INTO playlists VALUES (0, "Playlist", 0);

CREATE TABLE playlist_tracks (
   pid INTEGER UNSIGNED NOT NULL REFERENCES playlists(id),
   tid INTEGER UNSIGNED NOT NULL REFERENCES tracks(id)
);

CREATE TABLE meta_data (
   sync_timestamp TIMESTAMP NOT NULL UNIQUE,
   archive_size   VARCHAR(20),
   artist_count   INTEGER UNSIGNED NOT NULL DEFAULT 0,
   album_count    INTEGER UNSIGNED NOT NULL DEFAULT 0,
   track_count    INTEGER UNSIGNED NOT NULL DEFAULT 0,
   total_time     INTEGER UNSIGNED NOT NULL DEFAULT 0
);

CREATE TABLE ui (
   main_window_pos_x  INTEGER UNSIGNED,
   main_window_pos_y  INTEGER UNSIGNED,
   main_window_width  INTEGER UNSIGNED NOT NULL DEFAULT 640,
   main_window_height INTEGER UNSIGNED NOT NULL DEFAULT 480
);
INSERT INTO ui VALUES (NULL, NULL, 640, 480);

/* Table for genre mapping.  Includes ID3 v1.1 genres (0 <= genre.id <= 79) as
   well as WinAmp extenstions (80 <= genre.id <= 125) */
CREATE TABLE genres (
   id TINYINT UNSIGNED NOT NULL PRIMARY KEY,
   name VARCHAR(30) NOT NULL default ''
);

INSERT INTO genres VALUES (0, "Blues");
INSERT INTO genres VALUES (1, "Classic Rock");
INSERT INTO genres VALUES (2, "Country");
INSERT INTO genres VALUES (3, "Dance");
INSERT INTO genres VALUES (4, "Disco");
INSERT INTO genres VALUES (5, "Funk");
INSERT INTO genres VALUES (6, "Grunge");
INSERT INTO genres VALUES (7, "Hip-Hop");
INSERT INTO genres VALUES (8, "Jazz");
INSERT INTO genres VALUES (9, "Metal");
INSERT INTO genres VALUES (10, "New Age");
INSERT INTO genres VALUES (11, "Oldies");
INSERT INTO genres VALUES (12, "Other");
INSERT INTO genres VALUES (13, "Pop");
INSERT INTO genres VALUES (14, "R&B");
INSERT INTO genres VALUES (15, "Rap");
INSERT INTO genres VALUES (16, "Reggae");
INSERT INTO genres VALUES (17, "Rock");
INSERT INTO genres VALUES (18, "Techno");
INSERT INTO genres VALUES (19, "Industrial");
INSERT INTO genres VALUES (20, "Alternative");
INSERT INTO genres VALUES (21, "Ska");
INSERT INTO genres VALUES (22, "Death Metal");
INSERT INTO genres VALUES (23, "Pranks");
INSERT INTO genres VALUES (24, "Soundtrack");
INSERT INTO genres VALUES (25, "Euro-Techno");
INSERT INTO genres VALUES (26, "Ambient");
INSERT INTO genres VALUES (27, "Trip-Hop");
INSERT INTO genres VALUES (28, "Vocal");
INSERT INTO genres VALUES (29, "Jazz+Funk");
INSERT INTO genres VALUES (30, "Fusion");
INSERT INTO genres VALUES (31, "Trance");
INSERT INTO genres VALUES (32, "Classical");
INSERT INTO genres VALUES (33, "Instrumental");
INSERT INTO genres VALUES (34, "Acid");
INSERT INTO genres VALUES (35, "House");
INSERT INTO genres VALUES (36, "Game");
INSERT INTO genres VALUES (37, "Sound Clip");
INSERT INTO genres VALUES (38, "Gospel");
INSERT INTO genres VALUES (39, "Noise");
INSERT INTO genres VALUES (40, "AlternRock");
INSERT INTO genres VALUES (41, "Bass");
INSERT INTO genres VALUES (42, "Soul");
INSERT INTO genres VALUES (43, "Punk");
INSERT INTO genres VALUES (44, "Space");
INSERT INTO genres VALUES (45, "Meditative");
INSERT INTO genres VALUES (46, "Instrumental Pop");
INSERT INTO genres VALUES (47, "Instrumental Rock");
INSERT INTO genres VALUES (48, "Ethnic");
INSERT INTO genres VALUES (49, "Gothic");
INSERT INTO genres VALUES (50, "Darkwave");
INSERT INTO genres VALUES (51, "Techno-Industrial");
INSERT INTO genres VALUES (52, "Electronic");
INSERT INTO genres VALUES (53, "Pop-Folk");
INSERT INTO genres VALUES (54, "Eurodance");
INSERT INTO genres VALUES (55, "Dream");
INSERT INTO genres VALUES (56, "Southern Rock");
INSERT INTO genres VALUES (57, "Comedy");
INSERT INTO genres VALUES (58, "Cult");
INSERT INTO genres VALUES (59, "Gangsta Rap");
INSERT INTO genres VALUES (60, "Top 40");
INSERT INTO genres VALUES (61, "Christian Rap");
INSERT INTO genres VALUES (62, "Pop/Funk");
INSERT INTO genres VALUES (63, "Jungle");
INSERT INTO genres VALUES (64, "Native American");
INSERT INTO genres VALUES (65, "Cabaret");
INSERT INTO genres VALUES (66, "New Wave");
INSERT INTO genres VALUES (67, "Psychadelic");
INSERT INTO genres VALUES (68, "Rave");
INSERT INTO genres VALUES (69, "Showtunes");
INSERT INTO genres VALUES (70, "Trailer");
INSERT INTO genres VALUES (71, "Lo-Fi");
INSERT INTO genres VALUES (72, "Tribal");
INSERT INTO genres VALUES (73, "Acid Punk");
INSERT INTO genres VALUES (74, "Acid Jazz");
INSERT INTO genres VALUES (75, "Polka");
INSERT INTO genres VALUES (76, "Retro");
INSERT INTO genres VALUES (77, "Musical");
INSERT INTO genres VALUES (78, "Rock & Roll");
INSERT INTO genres VALUES (79, "Hard Rock");
INSERT INTO genres VALUES (80, "Folk");
INSERT INTO genres VALUES (81, "Folk-Rock");
INSERT INTO genres VALUES (82, "National Folk");
INSERT INTO genres VALUES (83, "Swing");
INSERT INTO genres VALUES (84, "Fast Fusion");
INSERT INTO genres VALUES (85, "Bebob");
INSERT INTO genres VALUES (86, "Latin");
INSERT INTO genres VALUES (87, "Revival");
INSERT INTO genres VALUES (88, "Celtic");
INSERT INTO genres VALUES (89, "Bluegrass");
INSERT INTO genres VALUES (90, "Avantgarde");
INSERT INTO genres VALUES (91, "Gothic Rock");
INSERT INTO genres VALUES (92, "Progressive Rock");
INSERT INTO genres VALUES (93, "Psychedelic Rock");
INSERT INTO genres VALUES (94, "Symphonic Rock");
INSERT INTO genres VALUES (95, "Slow Rock");
INSERT INTO genres VALUES (96, "Big Band");
INSERT INTO genres VALUES (97, "Chorus");
INSERT INTO genres VALUES (98, "Easy Listening");
INSERT INTO genres VALUES (99, "Acoustic");
INSERT INTO genres VALUES (100, "Humour");
INSERT INTO genres VALUES (101, "Speech");
INSERT INTO genres VALUES (102, "Chanson");
INSERT INTO genres VALUES (103, "Opera");
INSERT INTO genres VALUES (104, "Chamber Music");
INSERT INTO genres VALUES (105, "Sonata");
INSERT INTO genres VALUES (106, "Symphony");
INSERT INTO genres VALUES (107, "Booty Bass");
INSERT INTO genres VALUES (108, "Primus");
INSERT INTO genres VALUES (109, "Porn Groove");
INSERT INTO genres VALUES (110, "Satire");
INSERT INTO genres VALUES (111, "Slow Jam");
INSERT INTO genres VALUES (112, "Club");
INSERT INTO genres VALUES (113, "Tango");
INSERT INTO genres VALUES (114, "Samba");
INSERT INTO genres VALUES (115, "Folklore");
INSERT INTO genres VALUES (116, "Ballad");
INSERT INTO genres VALUES (117, "Power Ballad");
INSERT INTO genres VALUES (118, "Rhythmic Soul");
INSERT INTO genres VALUES (119, "Freestyle");
INSERT INTO genres VALUES (120, "Duet");
INSERT INTO genres VALUES (121, "Punk Rock");
INSERT INTO genres VALUES (122, "Drum Solo");
INSERT INTO genres VALUES (123, "A capella");
INSERT INTO genres VALUES (124, "Euro-House");
INSERT INTO genres VALUES (125, "Dance Hall");
INSERT INTO genres VALUES (126, "Goa");
INSERT INTO genres VALUES (127, "Drum & Bass");
INSERT INTO genres VALUES (128, "Club-House");
INSERT INTO genres VALUES (129, "Hardcore");
INSERT INTO genres VALUES (130, "Terror");
INSERT INTO genres VALUES (131, "Indie");
INSERT INTO genres VALUES (132, "BritPop");
INSERT INTO genres VALUES (133, "Negerpunk");
INSERT INTO genres VALUES (134, "Polsk Punk");
INSERT INTO genres VALUES (135, "Beat");
INSERT INTO genres VALUES (136, "Christian Gangsta Rap");
INSERT INTO genres VALUES (137, "Heavy Metal");
INSERT INTO genres VALUES (138, "Black Metal");
INSERT INTO genres VALUES (139, "Crossover");
INSERT INTO genres VALUES (140, "Contemporary Christian");
INSERT INTO genres VALUES (141, "Christian Rock");
INSERT INTO genres VALUES (142, "Merengue");
INSERT INTO genres VALUES (143, "Salsa");
INSERT INTO genres VALUES (144, "Thrash Metal");
INSERT INTO genres VALUES (145, "Anime");
INSERT INTO genres VALUES (146, "JPop");
INSERT INTO genres VALUES (147, "Synthpop");
INSERT INTO genres VALUES (255, "Unknown");
