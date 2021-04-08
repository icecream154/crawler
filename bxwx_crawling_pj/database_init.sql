CREATE TABLE IF NOT EXISTS novel_meta(
    novel_id INT UNSIGNED AUTO_INCREMENT,
    novel_name VARCHAR(30) NOT NULL,
    novel_author VARCHAR(30) NOT NULL,
    novel_chapter_num INT UNSIGNED,
    novel_root_page_url VARCHAR(255) NOT NULL,
    novel_type VARCHAR(10),
    PRIMARY KEY (novel_id)
)CHARSET=utf8;

CREATE TABLE IF NOT EXISTS novel_chapter(
    novel_id INT UNSIGNED NOT NULL,
    chapter_id INT UNSIGNED NOT NULL,
    chapter_title VARCHAR(30) NOT NULL,
    chapter_content TEXT NOT NULL,
    PRIMARY KEY (novel_id, chapter_id),
    FOREIGN KEY (novel_id) references novel_meta(novel_id)
)CHARSET=utf8;