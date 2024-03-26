create table if not exists Users (
    user_id integer primary key autoincrement,
    username varchar(255) not null
);

create table if not exists Times (
    time_id integer primary key autoincrement,
    user_id integer not null,
    time_each_assembly time not null,
    milliseconds int not null,
    foreign key (user_id) references Users(user_id)
);