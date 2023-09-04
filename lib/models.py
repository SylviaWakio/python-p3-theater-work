from sqlalchemy import ForeignKey, Column, Integer, String, MetaData, Boolean, update
from sqlalchemy.orm import relationship, backref, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

convention = {
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
}
metadata = MetaData(naming_convention=convention)

Base = declarative_base(metadata=metadata)

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer(), primary_key=True)
    character_name = Column(String())

    auditions = relationship('Audition', backref = backref('role'), cascade='all')

    def __repr__(self):
        return f'Role (id: {self.id}) - ' + \
            f'Character: {self.character_name} '
    
    def auditions(self):
        return session.query(Audition).filter(Audition.role_id == self.id).all() 
    
    def actors(self):
        return [audition.actor for audition in self.auditions] 
    
    def locations(self):
        return [audition.location for audition in self.auditions] 
    
    def lead(self, session:Session):
        hired_roles = session.query(Audition).filter(Audition.role_id == self.id, Audition.hired == True).all()
        if hired_roles:
            return hired_roles[0]
        else:
            return "No actor has been hired for this role."

    def understudy(self, session:Session):
        hired_auditions = session.query(Audition).filter(Audition.role_id == self.id, Audition.hired == True).all()
        if len(hired_auditions) > 1:
            return hired_auditions[1]
        else:
            return "No actor has been hired for understudy for this role."
 

class Audition(Base):
    __tablename__ = 'auditions'

    id = Column(Integer(), primary_key = True)
    actor = Column(String())
    location = Column(String())
    phone = Column(Integer())
    hired = Column(Boolean())
    
    role_id = Column(ForeignKey('roles.id'))

    def __repr__(self):
        return f'Audition(id: {self.id}: ' + \
            f'Actor: {self.actor},  ' + \
            f'Location: {self.location}, ' + \
            f'Phone: {self.phone}, ' + \
            f'Hired: {self.hired}, ' + \
            f'Role ID: {self.role_id}'
    
    @classmethod
    def role(self, session):
        role_name = session.query(Role.character_name).filter(Dev.id == self.role_id).scalar()
        return f'Auditioned for: {role.character_name}'
    
    def call_back(self, session: Session):
        update_stmt = update(Audition).where(Audition.id == self.id).values(hired=True)
        session.execute(update_stmt)
        session.commit()
        return self

if __name__ == '__main__':
    engine = create_engine('sqlite:///roles.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    audition = session.query(Audition).first()

    if audition:
        audition.call_back(session)
        print(audition)
    else:
        print(f"Audition with ID {audition_id} does not exist.")