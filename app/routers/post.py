from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, Response, status, APIRouter
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List, Optional
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", response_model=List[schemas.PostOut])
async def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user),
                    limit: int = 10, skip: int = 0, search: Optional[str] = ''):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).filter(
    #     models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    results_post_votes = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")
        ).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.owner_id == current_user.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    
    print(results_post_votes)
    # print(current_user.email)
    # return {"data": posts}
    # return posts

    # posts_with_votes = [
    #     {"Post": post, "votes": votes} for post, votes in results_post_votes
    # ]
    return results_post_votes

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
async def create_posts(post: schemas.PostCreate, 
                       db: Session = Depends(get_db), 
                       current_user: int = Depends(oauth2.get_current_user) ): # easy for testing
   
   # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, 
    #                (post.title, post.content, post.published))
    # conn.commit()
    # new_post = cursor.fetchone()
    
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    print('current_user:', current_user.email)
    try:
        new_post = models.Post( owner_id = current_user.id, **post.model_dump(exclude_unset=True))
        db.add(new_post)
        db.commit()
        db.refresh(new_post) 
        # return {"data": new_post}
        return new_post
    except Exception as e:
        print(f"Error occurred: {e}")

@router.get("/{id}", response_model=schemas.PostOut)
async def get_post(id: int, db: Session = Depends(get_db), 
                   current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id),)) # add las , (str(id),
    # post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    print('current_user.id', current_user.id, '',)
    post = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")
        ).join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    print(post)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    # return {"post_detail": post}
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s  RETURNING *""", (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    deleted_post = db.query(models.Post).filter(models.Post.id == id)

    post = deleted_post.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    deleted_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                response_model=schemas.PostResponse, 
                current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #                (post.title, post.content, post.published, str(id)),)
    # updated_post = cursor.fetchone()
    # conn.commit()

    updated_post = db.query(models.Post).filter(models.Post.id == id)

    post_query = updated_post.first()

    if post_query == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id {id} does not exist")
    if post_query.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorized to perform requested action")
    updated_post.update(post.model_dump(exclude_unset=True), synchronize_session=False)
    db.commit()
    # return {'data': updated_post.first()}
    return updated_post.first()
