<template>
    <v-navigation-drawer
    expand-on-hover
    rail
    >
        <v-list density="compact" nav>
            <v-list-item to="/Dashboard" prepend-icon="mdi-view-dashboard-outline" title="Dashboard"></v-list-item>
            <v-list-item to="/StudyForm" prepend-icon="mdi-form-select" title="User Studies"></v-list-item>
            <v-list-item to="/SessionForm" prepend-icon="mdi-crowd" title="Participant Sessions"></v-list-item>
            <v-list-item to="/DataAnalytics" prepend-icon="mdi-chart-box-outline" title="Data Analytics"></v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>