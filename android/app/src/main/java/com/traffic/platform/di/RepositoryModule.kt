package com.traffic.platform.di

import com.traffic.platform.data.remote.TrafficApi
import com.traffic.platform.data.repository.TrafficRepository
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {

    @Provides
    @Singleton
    fun provideTrafficRepository(api: TrafficApi): TrafficRepository = TrafficRepository(api)
}
