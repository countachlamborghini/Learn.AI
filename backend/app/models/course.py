from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    grade_level = Column(String(50), nullable=True)  # 9th, 10th, college, etc.
    subject = Column(String(100), nullable=True)
    
    # Course settings
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    max_students = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    tenant = relationship("Tenant", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    documents = relationship("Document", back_populates="course")

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', subject='{self.subject}')>"

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    role = Column(String(20), default="student")  # student, teacher, ta
    
    # Enrollment status
    is_active = Column(Boolean, default=True)
    enrolled_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, role='{self.role}')>"