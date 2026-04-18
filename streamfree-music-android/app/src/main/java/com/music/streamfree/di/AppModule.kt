package com.music.streamfree.di

import android.app.Application
import androidx.media3.exoplayer.ExoPlayer
import com.music.streamfree.data.ExtractorRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideExoPlayer(app: Application): ExoPlayer {
        return ExoPlayer.Builder(app).build()
    }

    @Provides
    @Singleton
    fun provideExtractorRepository(): ExtractorRepository {
        return ExtractorRepository()
    }
}
