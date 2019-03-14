CREATE TABLE dbo.TablePoints (
	ID int IDENTITY(1, 1) PRIMARY KEY,
	Pnt PointType)

INSERT INTO dbo.TablePoints (Pnt) VALUES (CONVERT(PointType, '3:4'))
INSERT INTO dbo.TablePoints (Pnt) VALUES (CONVERT(PointType, '-1:5'))
INSERT INTO dbo.TablePoints (Pnt) Values (CAST ('1:99' AS PointType))

SELECT ID, Pnt.ToString() as StringPoint, Pnt.X as X, Pnt.Y as Y FROM dbo.TablePoints