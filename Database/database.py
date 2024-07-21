import motor.motor_asyncio
from config import DATABASE_NAME, DATABASE_URI
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime

class Database:
    def __init__(self, uri, database_name):        
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users_col = self.db["users"]
        self.files_col = self.db.files
        self.media_info_col = self.db.media_info
        self.stats_col = self.db.stats
        self.banned_col = self.db["banned_users"]
        self.user_quality_selection_col = self.db['user_quality_selection']
        self.file_data_col = self.db['file_data']
        
    async def add_user(self, user_id: int, username: str):
        try:
            await self.users_col.update_one(
                {"user_id": user_id},
                {"$set": {
                    "username": username,
                    "joined_updates_channel": False,
                    "joined_group_channel": False
                }},
                upsert=True
            )
        except PyMongoError as e:
            print(f"An error occurred while updating the user: {e}")
            raise

      
 
    async def ban_user(self, user_id: int):
        try:
            await self.banned_col.update_one(
                {"user_id": user_id},
                {"$set": {"banned": True}},
                upsert=True
            )
        except PyMongoError as e:
            print(f"An error occurred while banning the user: {e}")
            raise    

    async def unban_user(self, user_id: int):
        try:
            await self.banned_col.delete_one({"user_id": user_id})
        except PyMongoError as e:
            print(f"An error occurred while unbanning user: {e}")
            raise

    async def count_users(self):
        try:
            return await self.users_col.count_documents({})
        except PyMongoError as e:
            print(f"An error occurred while counting users: {e}")
            raise

    async def count_banned_users(self):
        try:
            return await self.banned_col.count_documents({})
        except PyMongoError as e:
            print(f"An error occurred while counting banned users: {e}")
            raise

    async def get_user(self, user_id: int):
        try:
            return await self.users_col.find_one({"user_id": user_id})
        except PyMongoError as e:
            print(f"An error occurred while retrieving user: {e}")
            raise

    async def is_user_banned(self, user_id: int):
        try:
            banned_user = await self.banned_col.find_one({"user_id": user_id})
            return banned_user is not None
        except PyMongoError as e:
            print(f"An error occurred while checking if user is banned: {e}")
            raise

    async def update_user_membership(self, user_id: int, joined_updates_channel: bool, joined_group_channel: bool):
        try:
            await self.users_col.update_one(
                {"user_id": user_id},
                {"$set": {
                    "joined_updates_channel": joined_updates_channel,
                    "joined_group_channel": joined_group_channel
                }},
                upsert=True
            )
        except PyMongoError as e:
            print(f"An error occurred while updating user membership: {e}")
            raise  

  
          
    async def update_user_settings(self, user_id, settings):
        await self.users_col.update_one({'id': user_id}, {'$set': {'settings': settings}}, upsert=True)
        
    async def get_user_settings(self, user_id):
        default_settings = {
            'sample_video_duration': "Not set",
            'screenshots': "Not set",
            'thumbnail_path': None,
            'gofile_api_key': None,
            'gdrive_folder_id': None,
            'metadata_titles': {
                'video_title': '',
                'audio_title': '',
                'subtitle_title': ''
            }
        }
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', default_settings)
        return default_settings
       

    
            
    async def save_sample_video_settings(self, user_id, sample_video_duration, screenshots):
        await self.users_col.update_one(
            {'id': user_id}, 
            {'$set': {
                'settings.sample_video_duration': sample_video_duration,
                'settings.screenshots': screenshots
            }},
            upsert=True
        )

    async def get_sample_video_settings(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            settings = user.get('settings', {})
            sample_video_duration = settings.get('sample_video_duration', "Not set")
            screenshots = settings.get('screenshots', "Not set")
            return sample_video_duration, screenshots
        return "Not set", "Not set"
        
    async def save_gofile_api_key(self, user_id, api_key):
        await self.users_col.update_one({'id': user_id}, {'$set': {'settings.gofile_api_key': api_key}}, upsert=True)
    
    async def get_gofile_api_key(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('gofile_api_key')
        return None
        
    async def save_custom_name(self, user_id, custom_name):
        await self.users_col.update_one(
            {'id': user_id},
            {'$set': {'settings.custom_name': custom_name}},
            upsert=True
        )

    async def get_custom_name(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('custom_name')
        return None
        
    async def save_gdrive_folder_id(self, user_id, folder_id):
        await self.users_col.update_one({'id': user_id}, {'$set': {'settings.gdrive_folder_id': folder_id}}, upsert=True)
    
    async def get_gdrive_folder_id(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('gdrive_folder_id')
        return None
    
    async def save_metadata_titles(self, user_id, video_title, audio_title, subtitle_title):
        await self.users_col.update_one(
            {'id': user_id}, 
            {'$set': {
                'settings.metadata_titles.video_title': video_title,
                'settings.metadata_titles.audio_title': audio_title,
                'settings.metadata_titles.subtitle_title': subtitle_title
            }},
            upsert=True
        )
    
    async def get_metadata_titles(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('metadata_titles', {})
        return {}
    
    async def save_screenshots_count(self, user_id, screenshots_count):
        await self.users_col.update_one(
            {'id': user_id},
            {'$set': {'settings.screenshots_count': screenshots_count}},
            upsert=True
        )
    
    async def get_screenshots_count(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('screenshots_count')
        return None
    
    async def get_sample_video_duration(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('settings', {}).get('sample_video_duration')
        return None
    
    async def save_thumbnail(self, user_id, file_id):
        await self.files_col.update_one({'id': user_id}, {'$set': {'thumbnail_file_id': file_id}}, upsert=True)
        
    async def get_thumbnail(self, user_id):
        file_data = await self.files_col.find_one({'id': user_id})
        if file_data:
            return file_data.get('thumbnail_file_id')
        return None
    
    async def delete_thumbnail(self, user_id):
        await self.files_col.update_one({'id': user_id}, {'$unset': {'thumbnail_file_id': ""}})
    
    async def save_attach_photo(self, user_id, file_id):
        await self.files_col.update_one({'id': user_id}, {'$set': {'attach_photo_file_id': file_id}}, upsert=True)
    
    async def get_attach_photo(self, user_id):
        file_data = await self.files_col.find_one({'id': user_id})
        if file_data:
            return file_data.get('attach_photo_file_id')
        return None

    async def save_merge_state(self, user_id, merge_state):
        try:
            await self.merge_col.update_one(
                {'id': user_id},
                {'$set': {'merge_state': merge_state}},
                upsert=True
            )
        except Exception as e:
            print(f"Error saving merge state to database: {e}")
            # Handle the error accordingly (logging, exception handling, etc.)

    async def get_merge_state(self, user_id):
        merge_state = await self.merge_col.find_one({'id': user_id})
        if merge_state:
            return merge_state.get('merge_state', {})
        return {}

    async def clear_merge_state(self, user_id):
        try:
            await self.merge_col.delete_one({'id': user_id})
        except Exception as e:
            print(f"Error clearing merge state from database: {e}")
            # Handle the error accordingly (logging, exception handling, etc.)

    async def save_merged_file_info(self, user_id, output_filename, file_size):
        try:
            await self.users_col.update_one(
                {'id': user_id},
                {'$set': {
                    'merged_file_info': {
                        'output_filename': output_filename,
                        'file_size': file_size
                    }
                }},
                upsert=True
            )
        except Exception as e:
            print(f"Error saving merged file info to database: {e}")
            # Handle the error accordingly (logging, exception handling, etc.)

    async def get_merged_file_info(self, user_id):
        user = await self.users_col.find_one({'id': user_id})
        if user:
            return user.get('merged_file_info', {})
        return {}

    async def clear_merged_file_info(self, user_id):
        try:
            await self.users_col.update_one(
                {'id': user_id},
                {'$unset': {'merged_file_info': ""}}
            )
        except Exception as e:
            print(f"Error clearing merged file info from database: {e}")
            # Handle the error accordingly (logging, exception handling, etc.)

    async def save_new_filename(self, user_id, new_filename):
        # Save new filename information to MongoDB
        await self.files_col.update_one(
            {'id': user_id},
            {'$set': {'new_filename': new_filename}},
            upsert=True
        )

    async def get_new_filename(self, user_id):
        # Retrieve new filename information from MongoDB
        file_data = await self.files_col.find_one({'id': user_id})
        if file_data:
            return file_data.get('new_filename')
        return None
    
    async def save_screenshot_paths(self, user_id, screenshot_paths):
        result = await self.users_col.update_one(
            {'_id': user_id},
            {'$set': {'screenshot_paths': screenshot_paths}},
            upsert=True
        )
        return result

    async def get_screenshot_paths(self, user_id):
        user = await self.users_col.find_one({'_id': user_id})
        if user:
            return user.get('screenshot_paths', [])
        return []

    async def delete_screenshot_paths(self, user_id):
        result = await self.users_col.update_one(
            {'_id': user_id},
            {'$unset': {'screenshot_paths': ''}}
        )
        return result.modified_count > 0

    async def save_extracted_files(self, user_id, file_list):
        await self.files_col.update_one(
            {'id': user_id},
            {'$set': {'extracted_files': file_list}},
            upsert=True
        )

    async def get_extracted_files(self, user_id):
        file_data = await self.files_col.find_one({'id': user_id})
        if file_data:
            return file_data.get('extracted_files', [])
        return []

    async def save_user_quality_selection(self, user_id, selection_data):
        result = await self.user_quality_selection_col.update_one(
            {'user_id': user_id},
            {'$set': selection_data},
            upsert=True
        )
        return result

    async def get_user_quality_selection(self, user_id):
        selection_data = await self.user_quality_selection_col.find_one({'user_id': user_id})
        return selection_data

     # Function to store media info in MongoDB
    async def store_media_info_in_db(self, media_info):
        result = await self.media_info_col.insert_one(media_info)
        return result.inserted_id
        
    async def save_file_data(self, user_id, file_data):
        result = await self.file_data_col.update_one(
            {'user_id': user_id},
            {'$set': file_data},
            upsert=True
        )
        return result

   
    async def get_file_data(self, user_id):
        file_data = await self.file_data_col.find_one({'user_id': user_id})
        return file_data

    async def save_stats(self, stats):
        try:
            await self.stats_col.update_one(
                {'_id': 'server_stats'},
                {'$set': stats},
                upsert=True
            )
        except Exception as e:
            print(f"An error occurred while saving stats: {e}")

    async def get_stats(self):
        try:
            stats = await self.stats_col.find_one({'_id': 'server_stats'})
            if stats:
                return stats
            return {}
        except Exception as e:
            print(f"An error occurred while retrieving stats: {e}")
            return {}


    async def clear_database(self):
        # Drop all collections
        await self.users_col.drop()
        await self.files_col.drop()
        await self.media_info_col.drop()
        await self.stats_col.drop()
        await self.banned_col.drop()
        await self.user_quality_selection_col.drop()
        await self.file_data_col.drop()

                
    async def get_all_user_ids(self):
        try:
            cursor = self.users_col.find({}, {"user_id": 1})
            user_ids = await cursor.to_list(length=10000)
            return [user['user_id'] for user in user_ids if 'user_id' in user]
        except PyMongoError as e:
            print(f"An error occurred while retrieving all user IDs: {e}")
            raise
            
# Initialize the database instance
db = Database(DATABASE_URI, DATABASE_NAME)    

