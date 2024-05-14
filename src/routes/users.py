# from fastapi import APIRouter, HTTPException
# from config.firebase_storage import firebase_admin, db

# router = APIRouter()

# # Collection reference
# users_ref = db.collection("users")

# # Create a new user
# @router.post("/users/")
# async def create_user(user_data: dict):
#     try:
#         doc_ref = users_ref.add(user_data)
#         return {"message": "User created successfully", "id": doc_ref.id}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Get all users
# @router.get("/users/")
# async def get_users():
#     try:
#         users = [doc.to_dict() for doc in users_ref.stream()]
#         return {"users": users}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Get a single user by ID
# @router.get("/users/{user_id}")
# async def get_user(user_id: str):
#     try:
#         doc = users_ref.document(user_id).get()
#         if doc.exists:
#             return {"user": doc.to_dict()}
#         else:
#             raise HTTPException(status_code=404, detail="User not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Update a user
# @router.put("/users/{user_id}")
# async def update_user(user_id: str, user_data: dict):
#     try:
#         users_ref.document(user_id).set(user_data, merge=True)
#         return {"message": "User updated successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Delete a user
# @router.delete("/users/{user_id}")
# async def delete_user(user_id: str):
#     try:
#         users_ref.document(user_id).delete()
#         return {"message": "User deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
