USE SPEECHES
GO

--drop assembly
IF EXISTS (SELECT * FROM sys.assemblies WHERE [NAME] = 
	'CLRUDF')
	DROP ASSEMBLY CLRUDF
GO

------------------------------------------------------
--
--  Import the assembly containing my types
--
------------------------------------------------------
USE SPEECHES
CREATE ASSEMBLY CLRUDF
FROM 'C:\Users\chris\Documents\Projects\C#\CLRUDF\CLRUDF\bin\Debug\CLRUDF.dll'
WITH PERMISSION_SET = UNSAFE

USE SPEECHES
GO
CREATE FUNCTION CreateSpeechIndex(@filename nvarchar(256))
RETURNS TABLE (Term nvarchar(256), Frequency int)
AS
EXTERNAL NAME CLRUDF.[CLRUDF.SpeechParser].InitMethod
GO