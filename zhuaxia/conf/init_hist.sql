/*********************************
 * TABLE Hist
 *********************************/
CREATE TABLE History  (
        id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
		song_name TEXT NOT NULL,
		hq INTEGER NOT NULL DEFAULT 0,
        source INTEGER NOT NULL, //1:xiami  2: netease
		location TEXT NOT NULL,
		api_url TEXT , // not used right now
		dl_time DATETIME,
        PRIMARY KEY (id)
    );

CREATE INDEX idx_uniq_01 on history (song_id,hq,source);
