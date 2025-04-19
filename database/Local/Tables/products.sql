CREATE TABLE [dbo].[products]
(
  [id] INT IDENTITY(1,1) PRIMARY KEY,
  [name] NVARCHAR(255),
  [description] NVARCHAR(MAX),
  [price] DECIMAL(18,2),
  [image_url] NVARCHAR(2083)
);

GO
