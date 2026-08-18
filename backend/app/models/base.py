from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass

print("========Base Metadata==============")
print(Base.metadata)
print("========Base Table=================")
print(Base.metadata.tables)
print()
print("Registered tables:")
for table in Base.metadata.tables.values():
    print(table.name)
print("========Base End=================")

