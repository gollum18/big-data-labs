CREATE TABLE Locations (grid_location dbo.PointType)

INSERT INTO Locations (grid_location) VALUES ('3:2')
INSERT INTO Locations (grid_location) VALUES ('-1:1')
INSERT INTO Locations (grid_location) VALUES ('-1:-1')
INSERT INTO Locations (grid_location) VALUES ('-8:-9')
INSERT INTO Locations (grid_location) VALUES ('4:-9')

SELECT * FROM dbo.Locations
SELECT grid_location.X as "X", grid_location.Y as "Y", grid_location.ToString() AS "Point" FROM dbo.Locations

UPDATE dbo.Locations SET grid_location.X = 5 WHERE grid_location.Y < 0
SELECT grid_location.X as "X", grid_location.Y AS "Y", grid_location.ToString() AS "Point" FROM dbo.Locations