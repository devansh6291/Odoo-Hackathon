const DataMapper = {
    // Maps Backend 'registration_number' to Frontend 'regNumber'
    mapVehicle: (v) => ({
        id: v.id,
        regNumber: v.registration_number, 
        model: v.name_model,
        maxLoadCapacity: v.max_load_capacity, // Maps 'max_load_capacity' to 'maxLoadCapacity'
        odometer: v.odometer,
        status: v.status
    }),

    // Maps Backend 'license_expiry_date' to Frontend 'licenseExpiry'
    mapDriver: (d) => ({
        id: d.id,
        name: d.name,
        licenseNumber: d.license_number,
        licenseCategory: d.license_category,
        licenseExpiry: d.license_expiry_date, // Maps 'license_expiry_date' to 'licenseExpiry'
        contactNumber: d.contact_number,
        safetyScore: d.safety_score,
        status: d.status
    })
};