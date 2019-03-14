USE COMPANY
GO

--drop assembly
IF EXISTS (SELECT * FROM sys.assemblies WHERE [NAME] = 
	'CLRUDT_TYPES')
	DROP ASSEMBLY CLRUDT_TYPES
GO

------------------------------------------------------
--
--  Import the assembly containing my types
--
------------------------------------------------------
USE COMPANY
CREATE ASSEMBLY CLRUDT_Types
FROM 'C:\Users\chris\Documents\Projects\C#\CLRUDT_Types\bin\Debug\CLRUDT_Types.dll'
WITH PERMISSION_SET = SAFE

------------------------------------------------------
--
--  Create the PointType
--
------------------------------------------------------

CREATE TYPE dbo.PointType
EXTERNAL NAME CLRUDT_Types.[CLRUDT_Types.PointType]