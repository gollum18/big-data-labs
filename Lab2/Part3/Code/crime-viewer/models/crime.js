// File: ./models/crime.js

var mongoose = require('mongoose');

// define the crime schema
var crimeSchema = new mongoose.Schema({
    _id: mongoose.Schema.Types.ObjectId,
    category: String,
    call_groups: String,
    final_case_type: String,
    case_desc: String,
    occ_date: String,
    x_coordinate: Number,
    y_coordinate: Number,
    census_tract: Number
});

// export the model
module.exports = mongoose.model('crime', crimeSchema);