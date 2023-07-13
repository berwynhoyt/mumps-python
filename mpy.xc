$ydb_dist/plugin/mpy.so

version:  gtm_int_t mpy_version_number( ) : sigsafe
func: gtm_int_t mpy_func( I:gtm_string_t*, O:gtm_string_t* [1048576], I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t* )
funcRaw: gtm_int_t mpy_func_raw( I:gtm_string_t*, O:gtm_string_t* [1048576], I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t* )
eval: gtm_int_t mpy_eval( I:gtm_string_t*, O:gtm_string_t* [1048576] )
exec: gtm_int_t mpy_exec( I:gtm_string_t*, O:gtm_string_t* [1048576] )
compile: gtm_int_t mpy_compile( I:gtm_string_t*, I:gtm_string_t*, I:gtm_string_t*, O:gtm_string_t* [1048576], I:gtm_string_t* )
uncompile: gtm_int_t mpy_uncompile( I:gtm_string_t* ) : sigsafe
