USE SPEECHES;

-- Insert data into the table using the results of the table valued function
DECLARE @Term nvarchar(256), @Frequency int;
DECLARE index_cursor CURSOR
	FOR SELECT * FROM dbo.CreateSpeechIndex('C:\Projects\CIS 612 Lab2\MasterAllUnionAddress.txt') AS I;
OPEN index_cursor;

-- Empty the Term_Index table
DELETE FROM TERM_INDEX;

-- Move to the first term
FETCH NEXT FROM index_cursor
INTO @Term, @Frequency;

-- Update the database
WHILE @@FETCH_STATUS = 0
BEGIN
	INSERT INTO TERM_INDEX VALUES 
		(@Term, @Frequency);
	FETCH NEXT FROM index_cursor
	INTO @Term, @Frequency;
END

CLOSE index_cursor;
DEALLOCATE index_cursor;

-- Get the top 10 from the database
SELECT * FROM TERM_INDEX;